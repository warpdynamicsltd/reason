open Formula

let rec var_occurs_in_term var = function
  | Var x -> x = var
  | Const _ -> false
  | Func (_, terms) -> List.exists (var_occurs_in_term var) terms


let rec substitute_in_term var replacement t = 
  match t with
    | Var v -> if v = var then replacement else Var v
    | Const _ -> t
    | Func (f, args) -> Func (f, List.map (substitute_in_term var replacement) args)


let rec substitute_in_formula var replacement = function
    | True -> True
    | False -> False
    | Pred (p, args) -> Pred (p, List.map (substitute_in_term var replacement) args)
    | Not f -> Not (substitute_in_formula var replacement f)
    | And(a, b) -> And (substitute_in_formula var replacement a, substitute_in_formula var replacement b)
    | Or(a, b) -> Or (substitute_in_formula var replacement a, substitute_in_formula var replacement b)
    | Implies(a, b) -> Implies (substitute_in_formula var replacement a, substitute_in_formula var replacement b)
    | Iff(a, b) -> Iff (substitute_in_formula var replacement a, substitute_in_formula var replacement b)
    | Exists(v, f) when v = var -> Exists(v, f)
    | Exists(v, f) when not (var_occurs_in_term v replacement) && v != var -> Exists(v, substitute_in_formula var replacement f)
    | Exists(_, _) -> failwith "substitution not admissible"
    | Forall(v, f) when v = var -> Forall(v, f)
    | Forall(v, f) when not (var_occurs_in_term v replacement) && v != var -> Forall(v, substitute_in_formula var replacement f)
    | Forall(_, _) -> failwith "substitution not admissible"


let is_simple_axiom formula = 
  match formula with
    | Implies(a, b) when a = b -> true
    | _ -> failwith "Not an axiom"


