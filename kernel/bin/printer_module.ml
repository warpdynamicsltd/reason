open Types
(*open Kernel*)

(*open Yojson.Safe.Util*)

let rec string_of_term t =
  match t with
  | Var v -> v
  | Const c -> c
  | ContextConst c -> "context_" ^ Int.to_string c
  | SkolemConst lst -> "skolem _" ^ String.concat "_" (List.map Int.to_string lst) 
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

(* Helper function to parse a reference from JSON *)
let reference_of_json (json : Yojson.Safe.t) : reference =
  match json with
  | `Assoc [("type", `String "Ref"); ("name", _); ("args", `List indices_json)] ->
      let indices = List.map Yojson.Safe.Util.to_int indices_json in
      Ref indices
  | _ -> failwith "Invalid Reference JSON"


(* Recursive function to handle JSON -> term conversion *)
let rec term_of_json (json : Yojson.Safe.t) =
  match json with
  | `Assoc [("type", `String "Variable"); ("name", `String v)] -> Var v
  | `Assoc [("type", `String "Const"); ("name", `String c)] -> Const c
  | `Assoc [("type", `String "ContextConst"); ("name", `Int c)] -> ContextConst c
  | `Assoc [("type", `String "SkolemConst"); ("name", `List indices_json)] ->
      let indices = List.map Yojson.Safe.Util.to_int indices_json in
      SkolemConst indices
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


(* Convert term to JSON *)
let rec json_of_term (t : term) : Yojson.Safe.t =
  match t with
  | Var v -> 
      `Assoc [("type", `String "Variable"); ("name", `String v)]
  | Const c -> 
      `Assoc [("type", `String "Const"); ("name", `String c)]
  | ContextConst c ->
      `Assoc [("type", `String "ContextConst"); ("name", `Int c)]
  | SkolemConst lst ->
      `Assoc [("type", `String "SkolemConst"); ("name", `String ""); ("args", `List (List.map (fun i -> `Int i) lst))]
  | Func (f, args) -> 
      `Assoc [("type", `String "Function"); ("name", `String f); ("args", `List (List.map json_of_term args))]

(* Convert formula to JSON *)
let rec json_of_formula (formula : first_order_formula) : Yojson.Safe.t =
  match formula with
  | True -> 
      `Assoc [("type", `String "True")]
  | False -> 
      `Assoc [("type", `String "False")]
  | Pred (name, args) -> 
      `Assoc [("type", `String "Predicate"); ("name", `String name); ("args", `List (List.map json_of_term args))]
  | Not f -> 
      `Assoc [("type", `String "LogicConnective"); ("name", `String "NEG"); ("args", `List [json_of_formula f])]
  | Or (left, right) -> 
      `Assoc [("type", `String "LogicConnective"); ("name", `String "OR"); ("args", `List [json_of_formula left; json_of_formula right])]
  | And (left, right) -> 
      `Assoc [("type", `String "LogicConnective"); ("name", `String "AND"); ("args", `List [json_of_formula left; json_of_formula right])]
  | Implies (left, right) -> 
      `Assoc [("type", `String "LogicConnective"); ("name", `String "IMP"); ("args", `List [json_of_formula left; json_of_formula right])]
  | Iff (left, right) -> 
      `Assoc [("type", `String "LogicConnective"); ("name", `String "IFF"); ("args", `List [json_of_formula left; json_of_formula right])]
  | Forall (var, f) -> 
      let var_json = json_of_term (Var var) in
      `Assoc [("type", `String "LogicQuantifier"); ("name", `String "FORALL"); ("args", `List [var_json; json_of_formula f])]
  | Exists (var, f) -> 
      let var_json = json_of_term (Var var) in
      `Assoc [("type", `String "LogicQuantifier"); ("name", `String "EXISTS"); ("args", `List [var_json; json_of_formula f])]

(* Helper function to convert to JSON string *)
let formula_to_json_string (formula : first_order_formula) : string =
  json_of_formula formula |> Yojson.Safe.pretty_to_string

(* Helper function to convert from JSON string *)
let formula_from_json_string (json_str : string) : first_order_formula =
  json_str |> Yojson.Safe.from_string |> formula_of_json

let json_of_bool (b : bool) : Yojson.Safe.t = `Assoc [("type", `String "Bool"); ("name", `String "return"); ("args", `List [`Bool b])]

(*let step_of_json (json : Yojson.Safe.t) =
  match json with 
    | `Assoc [("type", `String "Axiom"); ("name", `String label); ("args", `List [`List formulas; `List terms])] ->
      Axiom(label, List.map formula_of_json formulas, List.map term_of_json terms)
    | `Assoc [("type", `String "Rule"); ("name", `String label); ("args", `List [`List indices; `List terms])] ->
      Rule(label, List.map to_int indices, List.map term_of_json terms)
    | _ -> failwith "Invalid Step JSON"

let proof_of_json (json : Yojson.Safe.t) =
  match json with 
    | `Assoc [("type", `String "Proof"); ("name", _); ("args", `List steps)] -> List.map step_of_json steps
    | _ -> failwith "Invalid Proof JSON"*)

(* Convert JSON to a 'statement' type *)
let rec statement_of_json (json : Yojson.Safe.t) : statement =
  match json with
  
  | `Assoc [("type", `String "AssumptionStmt"); ("name", _); ("args", `List[ref_json; formula_json])] ->
    let ref = reference_of_json ref_json in
    let formula = formula_of_json formula_json in
    AssumptionStmt {ref; formula}
  
  | `Assoc [("type", `String "AxiomStmt"); ("name", _); ("args", `List [ref_json; `String label; `List fofs_json; `List terms_json; formula_json])] ->
      let ref = reference_of_json ref_json in
      let fofs = List.map formula_of_json fofs_json in
      let terms = List.map term_of_json terms_json in
      let formula = formula_of_json formula_json in
      AxiomStmt {ref; label; fofs; terms; formula}

  | `Assoc [("type", `String "RuleStmt"); ("name", _); ("args", `List [ref_json; `String label; `List refs_json; `List terms_json; formula_json])] ->
      let ref = reference_of_json ref_json in
      let refs = List.map reference_of_json refs_json in
      let terms = List.map term_of_json terms_json in
      let formula = formula_of_json formula_json in
      RuleStmt {ref; label; refs; terms; formula}

  | `Assoc [("type", `String "BlockStmt"); ("name", _); ("args", `List [ref_json;  `List statements_json; formula_json])] ->
      let ref = reference_of_json ref_json in
      let statements = List.map statement_of_json statements_json in
      let formula = formula_of_json formula_json in
      BlockStmt {ref; statements; formula}

  | _ -> failwith "Invalid Statement JSON"





