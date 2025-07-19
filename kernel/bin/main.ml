open Printer_module
open Core

let command c f =
  let formula = formula_of_json f in
  match c with
    | "ToNnf" -> to_nnf formula
    | "ToCnf" -> to_cnf formula
    | "Skolemize" -> skolemize formula []
    | "Print" -> formula
    | _ -> failwith "Unknown Command"

let exec (json : Yojson.Safe.t) = 
  match json with 
    | `Assoc [("type", `String "Command"); ("name", `String c); ("args", `List [f])] -> command c f
    | _ -> failwith "Invalid formula JSON"


let () =
  let content = In_channel.input_all In_channel.stdin in
  let json = Yojson.Safe.from_string content in
  let out = string_of_formula (exec json) in
  Printf.printf "%s\n" out;;