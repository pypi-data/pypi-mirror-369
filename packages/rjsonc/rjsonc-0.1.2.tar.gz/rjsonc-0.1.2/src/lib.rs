use anyhow::{ Context, Result };

use pyo3::{ prelude::*, types::{ PyBool, PyDict, PyFloat, PyInt, PyList, PyNone, PyString } };
use ijson::{ IValue, ValueType };

#[pyfunction]
fn loads_str(py: Python<'_>, json: &str) -> Result<Py<PyAny>> {
    let value: IValue = serde_json5::from_str(json).context("ijson::IValue extraction")?;
    Ok(get_py(py, value)?)
}

#[pyfunction]
fn loads_bytes(py: Python<'_>, json: &[u8]) -> Result<Py<PyAny>> {
    let value: IValue = serde_json5::from_slice(json).context("ijson::IValue extraction")?;
    Ok(get_py(py, value)?)
}

fn get_py(py: Python<'_>, value: IValue) -> Result<Py<PyAny>> {
    match value.type_() {
        ValueType::Bool => Ok(PyBool::new(py, value.to_bool().unwrap()).extract::<Py<PyAny>>()?),
        ValueType::Null => Ok(PyNone::get(py).extract::<Py<PyAny>>()?),
        ValueType::Number => {
            let number = value.into_number().unwrap();
            if number.has_decimal_point() {
                Ok(PyFloat::new(py, number.to_f64().unwrap()).into_any().unbind())
            } else {
                Ok(PyInt::new(py, number.to_i64().unwrap()).into_any().unbind())
            }
        }
        ValueType::String =>
            Ok(PyString::new(py, value.as_string().unwrap().as_str()).into_any().unbind()),

        ValueType::Array => {
            let array = value.into_array().unwrap();
            let list = PyList::empty(py);

            for item in array {
                list.append(get_py(py, item)?)?;
            }

            Ok(list.into_any().unbind())
        }
        ValueType::Object => {
            let obj = value.into_object().unwrap();
            let dict = PyDict::new(py);

            for (key, value) in obj {
                dict.set_item(PyString::new(py, key.as_str()), get_py(py, value)?)?;
            }

            Ok(dict.into_any().unbind())
        }
    }
}

#[pymodule]
fn rjsonc(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(loads_str, m)?)?;
    m.add_function(wrap_pyfunction!(loads_bytes, m)?)?;
    Ok(())
}
