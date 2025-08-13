use std::{any::type_name, default};

use robot_behavior::{RobotException, RobotResult, deserialize_error};

use crate::robot_error::RobotError;

pub trait CommandSerde: Sized {
    fn to_string(&self) -> String;
    fn from_str(data: &str) -> RobotResult<Self>;
    fn try_default() -> Self;
    fn num_args() -> usize {
        1
    }
}

impl CommandSerde for RobotError {
    fn to_string(&self) -> String {
        serde_json::to_string(self).unwrap()
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        serde_json::from_str(data).map_err(deserialize_error::<RobotError, _>(data))
    }
    fn try_default() -> Self {
        Self::default()
    }
}

impl CommandSerde for () {
    fn to_string(&self) -> String {
        String::new()
    }
    fn from_str(_: &str) -> RobotResult<Self> {
        Ok(())
    }
    fn try_default() -> Self {}
    fn num_args() -> usize {
        0
    }
}

impl CommandSerde for bool {
    fn to_string(&self) -> String {
        format!("{}", if *self { 1 } else { 0 })
    }

    fn from_str(data: &str) -> RobotResult<Self> {
        match data {
            "0" => Ok(false),
            "1" => Ok(true),
            _ => Err(deserialize_error::<bool, _>(data)(())),
        }
    }

    fn try_default() -> Self {
        false
    }
}

impl CommandSerde for u8 {
    fn to_string(&self) -> String {
        format!("{self}")
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        data.parse().map_err(deserialize_error::<u8, _>(data))
    }
    fn try_default() -> Self {
        0
    }
}

impl CommandSerde for u16 {
    fn to_string(&self) -> String {
        format!("{self}")
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        data.parse().map_err(deserialize_error::<u16, _>(data))
    }
    fn try_default() -> Self {
        0
    }
}

impl CommandSerde for f64 {
    fn to_string(&self) -> String {
        format!("{self}")
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        data.parse().map_err(deserialize_error::<f64, _>(data))
    }
    fn try_default() -> Self {
        0.0
    }
}

impl<T1, T2> CommandSerde for (T1, T2)
where
    T1: CommandSerde,
    T2: CommandSerde,
{
    fn to_string(&self) -> String {
        format!("{},{}", self.0.to_string(), self.1.to_string())
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        let mut data = data.split(',');
        Ok((
            T1::from_str(data.next().unwrap())?,
            T2::from_str(data.next().unwrap())?,
        ))
    }
    fn try_default() -> Self {
        (T1::try_default(), T2::try_default())
    }
    fn num_args() -> usize {
        2
    }
}

impl<T1, T2, T3> CommandSerde for (T1, T2, T3)
where
    T1: CommandSerde,
    T2: CommandSerde,
    T3: CommandSerde,
{
    fn to_string(&self) -> String {
        format!(
            "{},{},{}",
            self.0.to_string(),
            self.1.to_string(),
            self.2.to_string()
        )
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        let mut data = data.split(',');
        Ok((
            T1::from_str(data.next().unwrap())?,
            T2::from_str(data.next().unwrap())?,
            T3::from_str(data.next().unwrap())?,
        ))
    }
    fn try_default() -> Self {
        (T1::try_default(), T2::try_default(), T3::try_default())
    }
    fn num_args() -> usize {
        3
    }
}

impl<const N: usize, T> CommandSerde for [T; N]
where
    T: CommandSerde + Copy,
{
    fn to_string(&self) -> String {
        self.iter()
            .map(|x| x.to_string())
            .collect::<Vec<_>>()
            .join(",")
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        let try_data = data
            .split(',')
            .map(|x| T::from_str(x).unwrap())
            .collect::<Vec<T>>()
            .try_into()
            .map_err(deserialize_error::<[T; N], _>(data))?;
        Ok(try_data)
    }
    fn try_default() -> Self {
        [T::try_default(); N]
    }
    fn num_args() -> usize {
        N
    }
}

impl CommandSerde for String {
    fn to_string(&self) -> String {
        self.clone()
    }
    fn from_str(data: &str) -> RobotResult<Self> {
        Ok(data.to_string())
    }
    fn try_default() -> Self {
        String::new()
    }
}
