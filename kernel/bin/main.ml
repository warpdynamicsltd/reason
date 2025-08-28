open Printer_module
(*open Transform*)
open Kernel

(*let command c f =
  let formula = formula_of_json f in
  match c with
    (*| "ToNnf" -> json_of_formula(to_nnf formula)
    | "ToCnf" -> json_of_formula(to_cnf formula)
    | "ToEnnf" -> json_of_formula(full_ennf formula)
    | "Skolemize" -> json_of_formula(skolemize formula [])*)
    | "Print" -> json_of_formula(formula)
    | _ -> failwith "Unknown Command"*)

(*let substitute var t f = 
  let formula = formula_of_json f in
  let term = term_of_json t in
  substitute_in_formula var term formula |> json_of_formula |> Yojson.Safe.pretty_to_string*)

let exec (json : Yojson.Safe.t) = 
  match json with 
    (*| `Assoc [("type", `String "Command"); ("name", `String "FinalTautology"); ("args", `List [proof])] -> 
      final_tautology (proof_of_json proof) |> json_of_formula |> Yojson.Safe.pretty_to_string*)
    | `Assoc [("type", `String "Command"); ("name", `String "KernelProof"); ("args", `List [proof])] ->
      proved_tautology (statement_of_json proof) |> json_of_formula |> Yojson.Safe.pretty_to_string
    (*| `Assoc [("type", `String "Command"); ("name", `String c); ("args", `List [f])] -> Yojson.Safe.pretty_to_string (command c f)*)
    (*| `Assoc [("type", `String "Command"); ("name", `String "Sub"); ("args", `List [`String var; t; f])] -> substitute var t f*)
    | _ -> failwith "Invalid JSON"


let () =
  let content = In_channel.input_all In_channel.stdin in
  let json = Yojson.Safe.from_string content in
  let out = exec json in
  Printf.printf "%s\n" out;;