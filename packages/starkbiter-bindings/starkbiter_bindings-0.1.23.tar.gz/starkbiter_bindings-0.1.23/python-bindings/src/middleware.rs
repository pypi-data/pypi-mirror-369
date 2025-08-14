#![allow(non_local_definitions)]
use std::{
    collections::HashMap,
    num::NonZeroU128,
    sync::{Arc, OnceLock},
};

use futures::{stream::Peekable, Stream, StreamExt};
use num_bigint::BigInt;
use pyo3::prelude::*;
use starkbiter_core::{
    environment::instruction::{self},
    middleware::{connection::Connection, traits::Middleware, StarkbiterMiddleware},
    tokens,
};
use starknet_accounts::{Account, SingleOwnerAccount};
use starknet_core::types::{self};
use starknet_devnet_types::rpc::gas_modification::GasModificationRequest;
use starknet_signers::{LocalWallet, SigningKey};
use tokio::sync::Mutex;
use tracing::trace;

use crate::environment::env_registry;

static MIDDLEWARES: OnceLock<Mutex<HashMap<String, Arc<StarkbiterMiddleware>>>> = OnceLock::new();
fn middlewares() -> &'static Mutex<HashMap<String, Arc<StarkbiterMiddleware>>> {
    MIDDLEWARES.get_or_init(|| Mutex::new(HashMap::new()))
}

static ACCOUNTS: OnceLock<Mutex<HashMap<String, SingleOwnerAccount<Connection, LocalWallet>>>> =
    OnceLock::new();
fn accounts() -> &'static Mutex<HashMap<String, SingleOwnerAccount<Connection, LocalWallet>>> {
    ACCOUNTS.get_or_init(|| Mutex::new(HashMap::new()))
}

type Subscription = Peekable<std::pin::Pin<Box<dyn Stream<Item = Event> + Send + Sync>>>;
type SubscriptionStore = HashMap<String, Mutex<Subscription>>;

static SUBSCRIPTIONS: OnceLock<Mutex<SubscriptionStore>> = OnceLock::new();
fn subscriptions() -> &'static Mutex<SubscriptionStore> {
    SUBSCRIPTIONS.get_or_init(|| Mutex::new(HashMap::new()))
}

#[pyclass]
#[derive(FromPyObject, Default)]
pub struct BlockId {
    #[pyo3(get, set)]
    pub number: Option<u64>,
    #[pyo3(get, set)]
    pub hash: Option<String>,
    #[pyo3(get, set)]
    pub tag: Option<String>,
}

#[allow(non_local_definitions)]
#[pymethods]
impl BlockId {
    #[staticmethod]
    pub fn from_number(number: u64) -> Self {
        BlockId {
            number: Some(number),
            ..Self::default()
        }
    }
    #[staticmethod]
    pub fn from_hash(hash: &str) -> Self {
        BlockId {
            hash: Some(hash.to_string()),
            ..Self::default()
        }
    }
    #[staticmethod]
    pub fn from_tag(tag: &str) -> Self {
        BlockId {
            tag: Some(tag.to_string()),
            ..Self::default()
        }
    }
}

impl TryFrom<BlockId> for types::BlockId {
    type Error = pyo3::PyErr;

    fn try_from(value: BlockId) -> Result<Self, Self::Error> {
        match value {
            BlockId {
                number: Some(number),
                hash: _,
                tag: _,
            } => Ok(types::BlockId::Number(number)),
            BlockId {
                number: _,
                hash: Some(hash),
                tag: _,
            } => Ok(types::BlockId::Hash(types::Felt::from_hex_unchecked(&hash))),
            BlockId {
                number: _,
                hash: _,
                tag: Some(tag),
            } => match tag.as_str() {
                "latest" => Ok(types::BlockId::Tag(types::BlockTag::Latest)),
                "pending" => Ok(types::BlockId::Tag(types::BlockTag::Pending)),
                _ => Err(pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Invalid block tag provided. Use 'latest' or 'pending'.",
                )),
            },
            _ => Err(pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "BlockId must have either a number, hash, or tag set",
            )),
        }
    }
}

#[pyfunction]
pub fn create_middleware<'p>(py: Python<'p>, label: &str) -> PyResult<&'p PyAny> {
    let label_local = label.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let envs_lock = env_registry().lock().await;
        let maybe_env = envs_lock.get(&label_local);

        if maybe_env.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Environment not found for: {:?}",
                label_local
            )));
        }

        let env = maybe_env.unwrap();

        let random_id = uuid::Uuid::new_v4().to_string();
        let middleware = StarkbiterMiddleware::new(env, Some(&random_id)).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to create middleware: {}",
                e
            ))
        })?;

        let mut middlewares_lock = middlewares().lock().await;
        middlewares_lock.insert(random_id.to_string(), middleware);

        Ok(random_id)
    })
}

#[pyfunction]
pub fn declare_contract<'p>(
    py: Python<'p>,
    middleware_id: &str,
    contract_json: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let contract_json_local = contract_json.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let class_hash = middleware
            .declare_contract(contract_json_local)
            .await
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to declare contract: {}",
                    e
                ))
            })?;

        Ok(class_hash.to_string())
    })
}

#[pyfunction]
pub fn create_account<'p>(
    py: Python<'p>,
    middleware_id: &str,
    class_hash: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let class_hash_id_local = class_hash.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock();
        let guard = middlewares_lock.await;
        let maybe_middleware = guard.get(middleware_id_local.as_str());

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let account = middleware
            .create_single_owner_account(
                Option::<SigningKey>::None,
                types::Felt::from_hex_unchecked(&class_hash_id_local),
                100000000,
            )
            .await
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyException, _>(format!(
                    "Can't create account: {:?}",
                    e
                ))
            })?;

        let mut accounts_lock = accounts().lock().await;

        let address = account.address().to_hex_string();

        accounts_lock.insert(address.clone(), account);

        Ok(address)
    })
}

#[pyfunction]
pub fn create_mock_account<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock();
        let guard = middlewares_lock.await;
        let maybe_middleware = guard.get(middleware_id_local.as_str());

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let maybe_account = middleware
            .create_mocked_account(types::Felt::from_hex_unchecked(&address_local))
            .await;

        let account = maybe_account.unwrap();

        let mut accounts_lock = accounts().lock().await;

        accounts_lock.insert(address_local.to_string(), account);

        Ok(address_local)
    })
}

#[pyclass]
#[derive(FromPyObject)]
pub struct Call {
    #[pyo3(get, set)]
    pub to: String,
    #[pyo3(get, set)]
    pub selector: String,
    #[pyo3(get, set)]
    pub calldata: Vec<BigInt>,
}

#[allow(non_local_definitions)]
#[pymethods]
impl Call {
    #[new]
    fn new(to: &str, selector: &str, calldata: Vec<BigInt>) -> Self {
        Call {
            to: to.to_string(),
            selector: selector.to_string(),
            calldata,
        }
    }
}

impl TryFrom<Call> for types::FunctionCall {
    type Error = pyo3::PyErr;

    fn try_from(value: Call) -> Result<types::FunctionCall, Self::Error> {
        let to = types::Felt::from_hex(&value.to).map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid 'to' address: {}",
                e
            ))
        })?;

        let selector = types::Felt::from_hex(&value.selector).map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid 'selector' value: {}",
                e
            ))
        })?;

        let calldata = value.calldata.iter().map(types::Felt::from).collect();

        Ok(types::FunctionCall {
            contract_address: to,
            entry_point_selector: selector,
            calldata,
        })
    }
}

#[pyfunction]
pub fn account_execute<'p>(py: Python<'p>, address: &str, calls: Vec<Call>) -> PyResult<&'p PyAny> {
    let address_local = address.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let accounts_lock = accounts().lock().await;

        let maybe_account = accounts_lock.get(address_local.as_str());

        if maybe_account.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Can't find account: {:?}",
                address_local
            )));
        }

        let account = maybe_account.unwrap();

        let calls = calls
            .iter()
            .map(|c| starknet_core::types::Call {
                to: types::Felt::from_hex_unchecked(&c.to),
                selector: types::Felt::from_hex_unchecked(&c.selector),
                calldata: c.calldata.iter().map(types::Felt::from).collect(),
            })
            .collect();

        let result = account.execute_v3(calls).send().await.map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to execute account calls: {}",
                e
            ))
        })?;

        Ok(result.transaction_hash.to_hex_string())
    })
}

#[pyfunction]
pub fn get_deployed_contract_address<'p>(
    py: Python<'p>,
    middleware_id: &str,
    tx_hash: &str,
) -> PyResult<&'p PyAny> {
    let tx_hash_local = tx_hash.to_string();
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock();
        let guard = middlewares_lock.await;
        let maybe_middleware = guard.get(middleware_id_local.as_str());

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let result = middleware
            .get_deployed_contract_address(types::Felt::from_hex_unchecked(&tx_hash_local))
            .await
            .map_err(|e| {
                PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "Failed to get deployed contract address: {}",
                    e
                ))
            })?;

        Ok(result.to_hex_string())
    })
}

#[pyfunction]
pub fn top_up_balance<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
    amount: u128,
    token: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();
    let token_local = token.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let token = tokens::TokenId::try_from(token_local.as_str()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid token ID provided: {}",
                e
            ))
        })?;

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to contract address: {:?} {:?}",
                &address_local, e
            ))
        })?;

        let middleware = maybe_middleware.unwrap();

        middleware
            .top_up_balance(address, amount, token)
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to top up balance: {}", e))
            })?;

        Ok(())
    })
}

#[pyfunction]
pub fn get_balance<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
    token: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();
    let token_local = token.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let token = tokens::TokenId::try_from(token_local.as_str()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid token ID provided: {}",
                e
            ))
        })?;

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to contract address: {:?} {:?}",
                &address_local, e
            ))
        })?;

        let middleware = maybe_middleware.unwrap();

        let result = middleware.get_balance(address, token).await.map_err(|e| {
            PyErr::new::<crate::ProviderError, _>(format!("Failed to top up balance: {}", e))
        })?;

        Ok(result)
    })
}

#[pyfunction]
pub fn set_storage<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
    key: &str,
    value: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();
    let key_local = key.to_string();
    let value_local = value.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to contract address: {:?} {:?}",
                &address_local, e
            ))
        })?;

        let key = types::Felt::from_hex(&key_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to felt252: {:?} {:?}",
                &key_local, e
            ))
        })?;

        let value = types::Felt::from_hex(&value_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to felt252: {:?} {:?}",
                &value_local, e
            ))
        })?;

        middleware
            .set_storage_at(address, key, value)
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to set storage: {}", e))
            })?;

        Ok(())
    })
}

#[pyfunction]
pub fn get_storage<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
    key: &str,
    block_id: BlockId,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();
    let key_local = key.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to contract address: {:?} {:?}",
                &address_local, e
            ))
        })?;

        let key = types::Felt::from_hex(&key_local).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Can't convert hex to felt252: {:?} {:?}",
                &key_local, e
            ))
        })?;

        let block_id = types::BlockId::try_from(block_id).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid block id: {:?}", e))
        })?;

        let data = middleware
            .get_storage_at(address, key, block_id)
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to get storage: {}", e))
            })?;

        Ok(data.to_hex_string())
    })
}

#[pyfunction]
pub fn call<'p>(
    py: Python<'p>,
    middleware_id: &str,
    call: Call,
    block_id: BlockId,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let block_id = types::BlockId::try_from(block_id).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid block id: {:?}", e))
        })?;

        let call = types::FunctionCall::try_from(call).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid call: {:?}", e))
        })?;

        let data = middleware.call(call, block_id).await.map_err(|e| {
            PyErr::new::<crate::ProviderError, _>(format!("Failed to perform call: {}", e))
        })?;

        let result: Vec<_> = data.iter().map(|i| i.to_hex_string()).collect();
        Ok(result)
    })
}

#[pyfunction]
pub fn impersonate<'p>(py: Python<'p>, middleware_id: &str, address: &str) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid 'to' address: {}",
                e
            ))
        })?;

        middleware.impersonate(address).await.map_err(|e| {
            PyErr::new::<crate::ProviderError, _>(format!("Failed to start impersonation: {}", e))
        })?;

        Ok(())
    })
}

#[pyfunction]
pub fn stop_impersonate<'p>(
    py: Python<'p>,
    middleware_id: &str,
    address: &str,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let address_local = address.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let address = types::Felt::from_hex(&address_local).map_err(|e| {
            pyo3::PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid 'to' address: {}",
                e
            ))
        })?;

        middleware
            .stop_impersonating_account(address)
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!(
                    "Failed to stop impersonation: {}",
                    e
                ))
            })?;

        Ok(())
    })
}

#[allow(clippy::too_many_arguments)]
#[pyfunction]
pub fn set_gas_price<'p>(
    py: Python<'p>,
    middleware_id: &str,
    gas_price_wei: Option<NonZeroU128>,
    gas_price_fri: Option<NonZeroU128>,
    data_gas_price_wei: Option<NonZeroU128>,
    data_gas_price_fri: Option<NonZeroU128>,
    l2_gas_price_wei: Option<NonZeroU128>,
    l2_gas_price_fri: Option<NonZeroU128>,
    generate_block: Option<bool>,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        middleware
            .set_next_block_gas(GasModificationRequest {
                gas_price_wei,
                gas_price_fri,
                data_gas_price_wei,
                data_gas_price_fri,
                l2_gas_price_wei,
                l2_gas_price_fri,
                generate_block,
            })
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to set gas price: {}", e))
            })?;

        Ok(())
    })
}

#[pyclass]
#[derive(Clone)]
pub struct Event {
    #[pyo3(get, set)]
    pub from_address: String,

    #[pyo3(get, set)]
    pub keys: Vec<String>,

    #[pyo3(get, set)]
    pub data: Vec<String>,

    #[pyo3(get, set)]
    pub block_hash: Option<String>,

    #[pyo3(get, set)]
    pub block_number: Option<u64>,

    #[pyo3(get, set)]
    pub transaction_hash: String,
}

impl TryFrom<&types::EmittedEvent> for Event {
    type Error = pyo3::PyErr;

    fn try_from(value: &types::EmittedEvent) -> Result<Self, Self::Error> {
        Ok(Self {
            from_address: value.from_address.to_hex_string(),
            keys: value.keys.iter().map(|i| i.to_hex_string()).collect(),
            data: value.data.iter().map(|i| i.to_hex_string()).collect(),
            block_hash: value.block_hash.map(|v| v.to_hex_string()),
            block_number: value.block_number,
            transaction_hash: value.transaction_hash.to_hex_string(),
        })
    }
}

#[pyfunction]
pub fn create_subscription<'p>(py: Python<'p>, middleware_id: &str) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let subscription = middleware.subscribe_to_flatten::<Event>().await;

        let mut subscriptions_lock = subscriptions().lock().await;
        let random_id = uuid::Uuid::new_v4().to_string();

        // TODO: remove peekable
        subscriptions_lock.insert(random_id.clone(), Mutex::new(subscription.peekable()));

        Ok(random_id)
    })
}

#[pyfunction]
pub fn poll_subscription<'p>(py: Python<'p>, subscription_id: &str) -> PyResult<&'p PyAny> {
    let subscription_id_local = subscription_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let subscriptions_lock = subscriptions().lock().await;
        let maybe_subscription = subscriptions_lock.get(&subscription_id_local);

        if maybe_subscription.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Subscription not found for: {:?}",
                &subscription_id_local
            )));
        }

        let subscription_lock = maybe_subscription.unwrap();
        let mut subscription = subscription_lock.lock().await;

        let maybe_next = subscription.next().await; // Advance the stream to the next event
        if maybe_next.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                "No events available in the subscription",
            ));
        }

        Ok(maybe_next.unwrap())
    })
}

#[pyclass]
#[derive(Clone)]
pub struct EventFilter {
    #[pyo3(get, set)]
    from_block_number: Option<u64>,
    #[pyo3(get, set)]
    from_block_tag: Option<String>,
    #[pyo3(get, set)]
    from_block_hash: Option<String>,

    #[pyo3(get, set)]
    to_block_number: Option<u64>,
    #[pyo3(get, set)]
    to_block_tag: Option<String>,
    #[pyo3(get, set)]
    to_block_hash: Option<String>,

    #[pyo3(get, set)]
    pub from_address: String,

    #[pyo3(get, set)]
    pub keys: Vec<Vec<String>>,
}

#[allow(clippy::too_many_arguments)]
#[allow(non_local_definitions)]
#[pymethods]
impl EventFilter {
    #[new]
    fn new(
        from_address: &str,
        keys: Vec<Vec<&str>>,

        // TODO(baitcode): for some reason pyo3 does
        // not support using python objects
        // in python objects
        from_block_number: Option<u64>,
        from_block_tag: Option<String>,
        from_block_hash: Option<String>,

        to_block_number: Option<u64>,
        to_block_tag: Option<String>,
        to_block_hash: Option<String>,
    ) -> Self {
        let keys = keys
            .iter()
            .map(|v| v.iter().map(|s| s.to_string()).collect::<Vec<_>>())
            .collect::<Vec<_>>();

        EventFilter {
            from_address: from_address.to_string(),
            keys,

            from_block_number,
            from_block_tag,
            from_block_hash,

            to_block_number,
            to_block_tag,
            to_block_hash,
        }
    }
}

impl From<&EventFilter> for instruction::EventFilter {
    fn from(value: &EventFilter) -> Self {
        let keys = value
            .keys
            .iter()
            .map(|v| {
                v.iter()
                    .map(|s| types::Felt::from_hex_unchecked(s))
                    .collect()
            })
            .collect();

        instruction::EventFilter {
            from_address: types::Felt::from_hex_unchecked(&value.from_address),
            keys,
        }
    }
}

impl From<&EventFilter> for types::EventFilter {
    fn from(value: &EventFilter) -> Self {
        let keys = value
            .keys
            .iter()
            .map(|v| {
                Some(
                    v.iter()
                        .map(|s| types::Felt::from_hex_unchecked(s))
                        .collect(),
                )
            })
            .collect();

        let from_block = match (
            value.from_block_number,
            &value.from_block_tag,
            &value.from_block_hash,
        ) {
            (Some(number), _, _) => Some(BlockId::from_number(number)),
            (None, Some(tag), _) => Some(BlockId::from_tag(tag)),
            (None, None, Some(hash)) => Some(BlockId::from_hash(hash)),
            _ => None,
        };

        let to_block = match (
            value.to_block_number,
            &value.to_block_tag,
            &value.to_block_hash,
        ) {
            (Some(number), _, _) => Some(BlockId::from_number(number)),
            (None, Some(tag), _) => Some(BlockId::from_tag(tag)),
            (None, None, Some(hash)) => Some(BlockId::from_hash(hash)),
            _ => None,
        };

        // TODO(baitcode): validate block id
        types::EventFilter {
            from_block: from_block.map(|b| b.try_into().unwrap()),
            to_block: to_block.map(|b| b.try_into().unwrap()),
            address: Some(types::Felt::from_hex_unchecked(&value.from_address)),
            keys,
        }
    }
}

#[pyfunction]
pub fn replay_block_with_txs<'p>(
    py: Python<'p>,
    middleware_id: &str,
    block_id: BlockId,
    has_events: Option<Vec<EventFilter>>,
    override_nonce: Option<bool>,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let block_id = types::BlockId::try_from(block_id).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid block id: {:?}", e))
        })?;

        // TODO(baitcode): validate event filters
        let has_events =
            has_events.map(|filters| filters.iter().map(|f| f.into()).collect::<Vec<_>>());

        middleware
            .replay_block_with_txs(block_id, has_events, override_nonce.unwrap_or(false))
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to replay block: {}", e))
            })?;

        Ok(())
    })
}

#[pyfunction]
pub fn get_block_events<'p>(
    py: Python<'p>,
    middleware_id: &str,
    from_block: Option<BlockId>,
    to_block: Option<BlockId>,
    from_address: Option<&str>,
    keys: Option<Vec<Vec<&str>>>,
) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();
    let from_address_local = from_address.map(|s| s.to_string());
    let keys_local = keys.map(|keys| {
        keys.iter()
            .map(|v| {
                v.iter()
                    .map(|s| types::Felt::from_hex_unchecked(s))
                    .collect()
            })
            .collect()
    });

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let events = middleware
            .get_all_events(
                from_block.map(|b| types::BlockId::try_from(b).unwrap()),
                to_block.map(|b| types::BlockId::try_from(b).unwrap()),
                from_address_local.map(|s| types::Felt::from_hex_unchecked(&s)),
                keys_local,
            )
            .await
            .map_err(|e| {
                PyErr::new::<crate::ProviderError, _>(format!("Failed to get block events: {}", e))
            })?;

        let results = events
            .iter()
            .map(Event::try_from)
            .flat_map(|r| r.ok())
            .collect::<Vec<_>>();

        Ok(results)
    })
}

#[pyfunction]
pub fn create_block<'p>(py: Python<'p>, middleware_id: &str) -> PyResult<&'p PyAny> {
    let middleware_id_local = middleware_id.to_string();

    pyo3_asyncio::tokio::future_into_py::<_, _>(py, async move {
        let middlewares_lock = middlewares().lock().await;
        let maybe_middleware = middlewares_lock.get(&middleware_id_local);

        if maybe_middleware.is_none() {
            return Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                "Middleware not found for: {:?}",
                &middleware_id_local
            )));
        }

        let middleware = maybe_middleware.unwrap();

        let block_hash = middleware.create_block().await.map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Failed to create block: {}",
                e
            ))
        })?;

        trace!("Created block with hash: {}", block_hash);

        Ok(block_hash.to_hex_string())
    })
}
