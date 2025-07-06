open Printer_module

(* Function to stringify a formula *)
let export_formula_string input_json =
  let json = Yojson.Safe.from_string input_json in
  let formula = formula_of_json json in
  string_of_formula formula
;;

let () =
  let content = In_channel.input_all In_channel.stdin in
  let out = export_formula_string content in
  Printf.printf "%s\n" out