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


let axiom = function
  | "L0" -> (function [a] -> Or(a, Not a) | _ -> failwith "unknown argument")
  | "L1" -> (function [a; b] -> Implies(a, (Implies(b, a))) | _ -> failwith "unknow argument")
  | _ -> failwith "unknow schema"

let rule = function
  | "modus-ponens" -> (
    function | [Implies(a, b); c] when c=a -> b | _ -> failwith "unknown argument"
  )
  | _ -> failwith "unknown rule"


type step = 
  | Axiom of string * first_order_formula list * first_order_formula
  | Rule of string * int list * first_order_formula

let nth_formula proof k = 
  match List.nth proof k with 
    | Axiom(_, _, formula) -> formula
    | Rule(_, _, formula) -> formula

let rec valid proof k =
  match List.nth proof k with
    | Axiom (label, formula_lst, formula) when (axiom label formula_lst = formula) -> true
    | Rule (label, index_lst, formula) when (
          (List.for_all (fun i -> i < k && valid proof i) index_lst) &&
          (rule label (List.map (nth_formula proof) index_lst) = formula)
        ) -> true
    | _ -> false

let is_valid proof = valid proof (List.length proof - 1);;


