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
  | "IFI" -> (function [a; b], [] -> Implies(Implies(a, b), Implies(Implies(b, a), Iff(a, b))) | _ -> axiom_error())
  | "IFO" -> (function [a; b], [] -> Implies(Iff(a, b), And(Implies(a, b), Implies(b, a))) | _ -> axiom_error())
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
  | "IDN" -> (function [a], [] -> a | _ -> failwith "illformed rule")
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


type reference =
  | Ref of int list

type statement = 
  | AssumptionStmt of 
    {
      ref: reference;
      formula: first_order_formula;
    }
  | AxiomStmt of 
    {
      ref: reference;
      label: string;
      fofs: first_order_formula list;
      terms: term list;
      formula: first_order_formula;
    }
  | RuleStmt of 
    {
      ref: reference;
      label: string;
      refs: reference list;
      terms: term list;
      formula: first_order_formula
    }
  | BlockStmt of 
    {
      ref: reference;
      (*assumption: first_order_formula;*)
      statements: statement list;
      formula: first_order_formula
    }

let formula_of_statement s = 
  match s with
    | AssumptionStmt {formula; _} -> formula
    | AxiomStmt {formula; _} -> formula
    | RuleStmt {formula; _} -> formula
    | BlockStmt {formula; _} -> formula

let rec get_statement proof = 
  match proof with 
    | BlockStmt {statements; _} -> 
          (fun ref -> 
            match ref with
            | Ref [] -> proof
            | Ref (head::tail) -> get_statement (List.nth statements head) (Ref tail))
    | _ -> (fun _ -> proof)

let get_formula proof ref = get_statement proof ref |> formula_of_statement

let rec reference_allowed current_ref ref = 
  match current_ref, ref with 
    | Ref [k], Ref [i] when i < k -> true
    | Ref (head::_), Ref [i] when i < head -> true
    | Ref (head::tail), Ref(head_ref::tail_ref) when head = head_ref -> reference_allowed (Ref tail) (Ref tail_ref)
    | _, _ -> false;;

let append ref i =
  match ref with
  | Ref lst -> Ref (lst @ [i])

let last_elem lst = List.nth lst (List.length lst - 1)  

let last_of_ref ref = match ref with Ref lst -> last_elem lst

let is_assumption_statement s = 
  match s with
    | AssumptionStmt _ -> true
    | _ -> false

let rec is_valid_conclusion proof r = 
  match get_statement proof r with
    | AssumptionStmt {ref; _} when ref = r && last_of_ref ref = 0 -> true
    | AxiomStmt {ref; label; fofs; terms; formula} when ref = r && formula = (axiom label (fofs, terms)) -> true
    | RuleStmt {ref; label; refs; terms; formula} when ref = r 
       && List.for_all (reference_allowed ref) refs
       && List.for_all (is_valid_conclusion proof) refs
        -> formula = (rule label (List.map (get_formula proof) refs, terms))
    | BlockStmt{ref; statements; formula} when ref = r && (List.length statements) > 0
      && 
        let statement0 = (List.hd statements) in
        let last_ref = append r (List.length statements - 1) in
        let f = last_elem statements |> formula_of_statement in
        (
          is_valid_conclusion proof (last_ref) && 
          formula = 
            if is_assumption_statement statement0 
            then 
              let assumption = statement0 |> formula_of_statement in
              Implies(assumption, f) 
            else f)

          -> true
    | _ -> false


  let proved_tautology proof = 
    match proof with
      | BlockStmt {formula;_} when (is_valid_conclusion proof (Ref[])) -> formula
      | _ -> failwith "invalid proof"