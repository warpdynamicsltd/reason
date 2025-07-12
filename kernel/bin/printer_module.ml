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
  | `Assoc [("type", `String "Variable"); ("name", `String v)] -> Var v
  | `Assoc [("type", `String "Const"); ("name", `String c)] -> Const c
  | `Assoc [("type", `String "Function"); ("name", `String f); ("args", `List args)] ->
      Func (f, List.map term_of_json args)
  | _ -> failwith "Invalid term JSON"

(* Function to parse JSON into `first_order_formula` *)
let rec formula_of_json (json : Yojson.Safe.t) =
  match json with
    | `Assoc [("type", `String "True")] -> True
    | `Assoc [("type", `String "False")] -> False
    | `Assoc [("type", `String "Predicate"); ("name", `String name); ("args", `List args)] ->
      Pred (name, List.map term_of_json args)
    | `Assoc [("type", `String "LogicConnective"); ("name", `String "NEG"); ("args", `List [f])] ->
      Not (formula_of_json f)
    | `Assoc [("type", `String "LogicConnective"); ("name", `String "OR"); ("args", `List [left; right])] ->
      Or (formula_of_json left, formula_of_json right)
    | `Assoc [("type", `String "LogicConnective"); ("name", `String "AND"); ("args", `List [left; right])] ->
      And (formula_of_json left, formula_of_json right)
    | `Assoc [("type", `String "LogicConnective"); ("name", `String "IMP"); ("args", `List [left; right])] ->
      Implies (formula_of_json left, formula_of_json right)
    | `Assoc [("type", `String "LogicConnective"); ("name", `String "IFF"); ("args", `List [left; right])] ->
      Iff (formula_of_json left, formula_of_json right)
    | `Assoc [("type", `String "LogicQuantifier"); ("name", `String "FORALL"); ("args", `List [v; formula])] ->
      (match term_of_json v with 
        | Var(name) -> Forall(name, formula_of_json formula)
        | _ -> failwith "Invalid formula JSON")
    | `Assoc [("type", `String "LogicQuantifier"); ("name", `String "EXISTS"); ("args", `List [v; formula])] ->
      (match term_of_json v with 
        | Var(name) -> Exists(name, formula_of_json formula)
        | _ -> failwith "Invalid formula JSON")
    | _ -> failwith "Invalid formula JSON"