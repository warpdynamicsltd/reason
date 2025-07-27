open Formula

let rec var_occurs_in_term var = function
  | Var v -> v = var
  | Const _ -> false
  | Func (_, terms) -> List.exists (var_occurs_in_term var) terms

let rec var_occurs_free_in_formula var = function
  | True -> false
  | False -> false
  | Pred(_, args) -> List.exists (var_occurs_in_term var) args
  | Not f -> var_occurs_free_in_formula var f
  | And(a, b) -> (var_occurs_free_in_formula var a) || (var_occurs_free_in_formula var b)
  | Or(a, b) -> (var_occurs_free_in_formula var a) || (var_occurs_free_in_formula var b)
  | Implies(a, b) -> (var_occurs_free_in_formula var a) || (var_occurs_free_in_formula var b)
  | Iff(a, b) -> (var_occurs_free_in_formula var a) || (var_occurs_free_in_formula var b)
  | Exists(v, f) -> not (v = var) && var_occurs_free_in_formula var f
  | Forall(v, f) -> not (v = var) && var_occurs_free_in_formula var f 

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

let axiom_error = function () -> failwith "illformed axiom"

let axiom = function
  | "LEM" -> (function [a], [] -> Or(a, Not a) | _, _ -> axiom_error())
  | "IMP" -> (function [a; b], [] -> Implies(a, (Implies(b, a))) | _ -> axiom_error())
  | "TRN" -> (function [a; b1; b2], [] -> Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2))) | _ -> axiom_error())
  | "ANL" -> (function [a; b], [] -> Implies(And(a, b), a) | _ -> axiom_error())
  | "ANR" -> (function [a; b], [] -> Implies(And(a, b), b) | _ -> axiom_error())
  | "AND" -> (function [a; b], [] -> Implies(a, Implies(b, And(a, b))) | _ -> axiom_error())
  | "ORL" -> (function [a; b], [] -> Implies(a, Or(a, b)) | _ -> axiom_error())
  | "ORR" -> (function [a; b], [] -> Implies(b, Or(a, b)) | _ -> axiom_error())
  | "DIS" -> (function [a; b; c], [] -> Implies(Implies(a, c), Implies(Implies(b, c), Implies(Or(a, b), c))) | _ -> axiom_error())
  | "CON" -> (function [a; b], [] -> Implies(Not a, Implies(a, b)) | _ -> axiom_error())
  | "ALL" -> (function [a], [t; Var(v)] -> Implies(Forall(v, a), substitute_in_formula v t a) | _ -> axiom_error())
  | "EXT" -> (function [a], [t; Var(v)] -> Implies(substitute_in_formula v t a, Exists(v, a)) | _ -> axiom_error())
  | "ALH" -> (
                function 
                  | [a; b], [Var(v)] when not (var_occurs_free_in_formula v a) -> 
                    Implies(Forall(v, Implies(a, b)), Implies(a, Forall(v, b)))  
                  | _ -> axiom_error()
              )
  | "EXH" -> (
                function 
                  | [a; b], [Var(v)] when not (var_occurs_free_in_formula v a) -> 
                    Implies(Forall(v, Implies(b, a)), Implies(Exists(v, b), a))  
                  | _ -> axiom_error()
              )
  | _ -> failwith "unknown schema"

let rule = function
  | "MOD" -> (function [Implies(a, b); c], [] when c=a -> b | _ -> failwith "illformed rule")
  | "GEN" -> (function [a], [Var(v)] -> Forall(v, a) | _ -> failwith "illformed rule")
  | _ -> failwith "unknown rule"


type step = 
  | Axiom of string * first_order_formula list * term list
  | Rule of string * int list * term list

let tautology proof =
  let proof_array = Array.of_list proof in
  let memo = Array.make (List.length proof) None in
  let rec nth_tautology n =
    match memo.(n) with 
      | Some res -> res
      | None ->
        let res =
          match proof_array.(n) with 
            | Axiom(label, formula_lst, term_lst) -> axiom label (formula_lst, term_lst)
            | Rule(label, index_lst, term_lst) 
                when List.for_all (fun i -> i < n) index_lst -> rule label (List.map (nth_tautology) index_lst, term_lst)
            | _ -> failwith "invalid proof" 
        in
        memo.(n) <- Some res;
        res
  in
  nth_tautology
    

let final_tautology proof = tautology proof (List.length proof - 1)


