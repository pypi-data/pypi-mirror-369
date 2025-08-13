use proc_macro::TokenStream;
use quote::quote;
use syn::{DeriveInput, parse_macro_input};

extern crate proc_macro;

#[proc_macro_derive(CommandSerde)]
pub fn robot_serde_derive(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;
    let fields = if let syn::Data::Struct(s) = &input.data {
        &s.fields
    } else {
        panic!("CommandSerde can only be derived for structs");
    };

    // 生成 to_string 实现
    let to_string_impl = fields.iter().map(|f| {
        let name = &f.ident;
        quote! {
            CommandSerde::to_string(&self.#name)
        }
    });

    // 生成字段解析逻辑
    let mut from_str_blocks = Vec::new();
    let mut field_inits = Vec::new();

    for field in fields.iter() {
        let field_ident = &field.ident;
        let field_ty = &field.ty;

        from_str_blocks.push(quote! {
            // 计算当前类型需要的参数数量
            let needed = <#field_ty as CommandSerde>::num_args();
            if current_index + needed > parts.len() {
                return Err(RobotException::DeserializeError(format!("invalid number of arguments of {}", stringify!(#name))));
            }

            // 合并需要的参数部分
            let part = if needed > 1 {
                parts[current_index..current_index + needed].join(",")
            } else {
                parts[current_index].to_string()
            };

            // 解析字段值
            let #field_ident = <#field_ty as CommandSerde>::from_str(&part)?;
            current_index += needed;
        });

        field_inits.push(quote! { #field_ident });
    }

    // 生成默认值实现
    let try_default_impl = fields.iter().map(|f| {
        let name = &f.ident;
        let ty = &f.ty;
        quote! {
            #name: <#ty>::try_default()
        }
    });

    // 生成参数数量统计
    let num_args_impl = fields.iter().map(|f| {
        let ty = &f.ty;
        quote! {
            <#ty as CommandSerde>::num_args()
        }
    });

    let expanded = quote! {
        impl CommandSerde for #name {
            fn to_string(&self) -> String {
                vec![#(#to_string_impl),*].join(",")
            }

            fn from_str(s: &str) -> RobotResult<Self> {
                let parts: Vec<&str> = s.split(',').collect();
                let mut current_index = 0;

                #(#from_str_blocks)*

                if current_index != parts.len() {
                    return Err(RobotException::DeserializeError(format!("invalid number of arguments of {}", stringify!(#name))));
                }

                Ok(Self {
                    #(#field_inits),*
                })
            }

            fn try_default() -> Self {
                Self {
                    #(#try_default_impl),*
                }
            }

            fn num_args() -> usize {
                #(#num_args_impl)+*
            }
        }
    };

    TokenStream::from(expanded)
}
