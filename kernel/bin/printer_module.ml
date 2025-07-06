open Formula

let rec string_of_term t =
  match t with
  | Var v -> v
  | Const c -> c
  | Func (f, args) ->
      f ^ "(" ^ (String.concat ", " (List.map string_of_term args)) ^ ")"

let rec string_of_formula f =
  match f with
  | True -> "⊤"
  | False -> "⊥"
  | Pred (name, args) ->
      name ^ "(" ^ (String.concat ", " (List.map string_of_term args)) ^ ")"
  | Not f1 -> "¬(" ^ string_of_formula f1 ^ ")"
  | And (f1, f2) -> "(" ^ string_of_formula f1 ^ " ∧ " ^ string_of_formula f2 ^ ")"
  | Or (f1, f2) -> "(" ^ string_of_formula f1 ^ " ∨ " ^ string_of_formula f2 ^ ")"
  | Implies (f1, f2) -> "(" ^ string_of_formula f1 ^ " → " ^ string_of_formula f2 ^ ")"
  | Iff (f1, f2) -> "(" ^ string_of_formula f1 ^ " ↔ " ^ string_of_formula f2 ^ ")"
  | Forall (v, f1) -> "∀" ^ v ^ ".(" ^ string_of_formula f1 ^ ")"
  | Exists (v, f1) -> "∃" ^ v ^ ".(" ^ string_of_formula f1 ^ ")"
;;


(* Recursive function to handle JSON -> term conversion *)
let rec term_of_json (json : Yojson.Safe.t) =
  match json with
  | `Assoc [("type", `String "Var"); ("name", `String v)] -> Var v
  | `Assoc [("type", `String "Const"); ("name", `String c)] -> Const c
  | `Assoc [("type", `String "Func"); ("name", `String f); ("args", `List args)] ->
      Func (f, List.map term_of_json args)
  | _ -> failwith "Invalid term JSON"

(* Helper to fold a JSON list into nested binary operations *)
let rec fold_binary op_constructor formulas =
  match formulas with
  | [] -> failwith "Invalid empty list for binary operation"
  | [single] -> formula_of_json single
  | first :: rest -> op_constructor (formula_of_json first) (fold_binary op_constructor rest)

(* Function to parse JSON into `first_order_formula` *)
and formula_of_json (json : Yojson.Safe.t) =
  match json with
  | `Assoc [("type", `String "True")] -> True
  | `Assoc [("type", `String "False")] -> False
  | `Assoc [("type", `String "Pred"); ("name", `String name); ("args", `List args)] ->
      Pred (name, List.map term_of_json args)
  | `Assoc [("type", `String "Not"); ("formula", subformula)] ->
      Not (formula_of_json subformula)
  | `Assoc [("type", `String "And"); ("formulas", `List formulas)] ->
      fold_binary (fun a b -> And (a, b)) formulas
  | `Assoc [("type", `String "Or"); ("formulas", `List formulas)] ->
      fold_binary (fun a b -> Or (a, b)) formulas
  | `Assoc [("type", `String "Implies"); ("left", left); ("right", right)] ->
      Implies (formula_of_json left, formula_of_json right)
  | `Assoc [("type", `String "Iff"); ("left", left); ("right", right)] ->
      Iff (formula_of_json left, formula_of_json right)
  | `Assoc [("type", `String "Forall"); ("variable", `String v); ("formula", subformula)] ->
      Forall (v, formula_of_json subformula)
  | `Assoc [("type", `String "Exists"); ("variable", `String v); ("formula", subformula)] ->
      Exists (v, formula_of_json subformula)
  | _ -> failwith "Invalid formula JSON"