open Types

let rec var_occurs_in_term var = function
  | Var v -> v = var
  | Const _ -> false
  | ContextConst _ -> false
  | SkolemConst _ -> false
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

(* Add at the top if not present *)
module StringSet = Set.Make(String)

(* Collect free variables from a term *)
let rec free_vars_term term : StringSet.t =
  match term with
  | Var x -> StringSet.singleton x
  | Const _ | ContextConst _ | SkolemConst _ -> StringSet.empty
  | Func (_, args) ->
      List.fold_left
        (fun vars arg -> StringSet.union vars (free_vars_term arg))
        StringSet.empty args

(* Main function: collect free variables from a first_order_formula *)
let rec free_vars_formula formula : StringSet.t =
  match formula with
  | True | False -> StringSet.empty
  | Pred (_, terms) ->
      List.fold_left
        (fun vars t -> StringSet.union vars (free_vars_term t))
        StringSet.empty terms
  | Not f -> free_vars_formula f
  | And (f1, f2)
  | Or (f1, f2)
  | Implies (f1, f2)
  | Iff (f1, f2) ->
      StringSet.union (free_vars_formula f1) (free_vars_formula f2)
  | Forall (x, f)
  | Exists (x, f) ->
      let vars = free_vars_formula f in
      StringSet.remove x vars

let rec substitute_in_term var replacement t = 
  match t with
    | Var v -> if v = var then replacement else Var v
    | Const _ -> t
    | ContextConst _ -> t
    | SkolemConst _ -> t
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

let rec substitute_context_const_in_term index replacement t = 
  match t with
    | Var _ -> t
    | Const _ -> t
    | ContextConst i -> if i = index then replacement else ContextConst i
    | SkolemConst _ -> t
    | Func (f, args) -> Func (f, List.map (substitute_context_const_in_term index replacement) args)


let rec substitute_context_const_in_formula index replacement = function
    | True -> True
    | False -> False
    | Pred (p, args) -> Pred (p, List.map (substitute_context_const_in_term index replacement) args)
    | Not f -> Not (substitute_context_const_in_formula index replacement f)
    | And(a, b) -> And (substitute_context_const_in_formula index replacement a, substitute_context_const_in_formula index replacement b)
    | Or(a, b) -> Or (substitute_context_const_in_formula index replacement a, substitute_context_const_in_formula index replacement b)
    | Implies(a, b) -> Implies (substitute_context_const_in_formula index replacement a, substitute_context_const_in_formula index replacement b)
    | Iff(a, b) -> Iff (substitute_context_const_in_formula index replacement a, substitute_context_const_in_formula index replacement b)
    | Exists(v, f) when not (var_occurs_in_term v replacement) -> substitute_context_const_in_formula index replacement f
    | Exists(_, _) -> failwith "substitution not admissible"
    | Forall(v, f) when not (var_occurs_in_term v replacement) -> substitute_context_const_in_formula index replacement f
    | Forall(_, _) -> failwith "substitution not admissible"

let substitute_context_const_in_formula_by_var index var formula = substitute_context_const_in_formula index (Var var) formula

let axiom_error = function () -> failwith "illformed axiom"

let axiom = function
  | "LEM" -> (function [a], [] -> Or(a, Not a) | _, _ -> axiom_error())
  | "IMP" -> (function [a; b], [] -> Implies(a, (Implies(b, a))) | _ -> axiom_error())
  (*| "TRN" -> (function [a; b1; b2], [] -> Implies(Implies(a, Implies(b1, b2)), Implies(Implies(a, b1), Implies(a, b2))) | _ -> axiom_error()) *)
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
  (*| "ALH" -> (
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
              )*)
  | _ -> failwith "unknown schema"

let rule = function
  | "IDN" -> (function [a], [] -> a | _ -> failwith "illformed rule")
  | "MOD" -> (function [Implies(a, b); c], [] when c=a -> b | _ -> failwith "illformed rule")
  | "GEN" -> (function [a], [Var(v)] -> Forall(v, a) | _ -> failwith "illformed rule")
  | "CTV" -> (function [a], [ContextConst(index); Var(v)] -> substitute_context_const_in_formula_by_var index v a | _ -> failwith "illformed rule")
  | "SKO" -> (function [Exists(v, a)], [SkolemConst(ref_seq); Var v1] when v=v1 -> substitute_in_formula v (SkolemConst ref_seq) a | _ -> failwith "illformed rule")
  | _ -> failwith "unknown rule"


(*type step = 
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
    

let final_tautology proof = tautology proof (List.length proof - 1)*)

let max_list lst =
  match lst with
  | [] -> -1
  | hd :: tl -> List.fold_left max hd tl


let rec max_context_const_index_of_term t = 
  match t with
    | Var _ -> -1
    | Const _ -> -1
    | ContextConst c -> c
    | SkolemConst _ -> -1
    | Func (_, terms) -> max_list (List.map max_context_const_index_of_term terms)


let rec max_context_const_index_of_formula f =
  match f with
    | True -> -1
    | False -> -1
    | Pred (_, args) -> max_list (List.map max_context_const_index_of_term args)
    | Not f1 -> max_context_const_index_of_formula f1
    | And (f1, f2)
    | Or (f1, f2)
    | Implies (f1, f2)
    | Iff (f1, f2) -> max (max_context_const_index_of_formula f1) (max_context_const_index_of_formula f2)
    | Exists (_, f1)
    | Forall (_, f1) -> max_context_const_index_of_formula f1


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

let rec (>>) current_ref ref = 
  match current_ref, ref with 
    | Ref [k], Ref [i] when i < k -> true
    | Ref (head::_), Ref [i] when i < head -> true
    | Ref (head::tail), Ref(head_ref::tail_ref) when head = head_ref -> Ref tail >> Ref tail_ref
    | _, _ -> false;;

let (>>=) r1 r2 = r1 >> r2 || r1 = r2

let rec is_suffix r1 r2 =
  match r1, r2 with
    | Ref [], Ref _ -> true
    | Ref (head1::tail1), Ref (head2::tail2) when head1 = head2 -> is_suffix (Ref tail1) (Ref tail2)
    | _, _ -> false
 
let append ref i =
  match ref with
  | Ref lst -> Ref (lst @ [i])

let last_elem lst = List.nth lst (List.length lst - 1)

let last_of_ref ref = match ref with Ref lst -> last_elem lst

let context_depth_of_ref ref = match ref with Ref lst -> List.length lst - 1

let rec var_accurs_free_in_assumptions proof r var = 
  match proof with
    | AssumptionStmt({ref; formula;_}) when r >> ref -> var_occurs_free_in_formula var formula
    | BlockStmt {ref; statements;_} when is_suffix ref r -> List.exists (fun s -> var_accurs_free_in_assumptions s r var) statements
    | _ -> false


let rec skolem_const_compatible_with_ref_in_term ref t =
    match t with
      | Var _ -> true
      | Const _ -> true
      | ContextConst _ -> true
      | SkolemConst seq -> ref >>= Ref seq
      | Func (_, terms) -> List.for_all (skolem_const_compatible_with_ref_in_term ref) terms

let rec skolem_const_compatible_with_ref_in_formula ref f =
    match f with
      | True -> true
      | False -> true
      | Pred (_, args) -> List.for_all (skolem_const_compatible_with_ref_in_term ref) args
      | Not f1 -> skolem_const_compatible_with_ref_in_formula ref f1
      | And (f1, f2)
      | Or (f1, f2)
      | Implies (f1, f2)
      | Iff (f1, f2) -> skolem_const_compatible_with_ref_in_formula ref f1 && skolem_const_compatible_with_ref_in_formula ref f2
      | Exists (_, f1)
      | Forall (_, f1) -> skolem_const_compatible_with_ref_in_formula ref f1

let formula_match_ref ref formula = 
  max_context_const_index_of_formula formula <= context_depth_of_ref ref
  && skolem_const_compatible_with_ref_in_formula ref formula

  let asm_formula_match_ref ref formula = 
  skolem_const_compatible_with_ref_in_formula ref formula 
  && max_context_const_index_of_formula formula < context_depth_of_ref ref

let ctv_rule_constrain ref terms = 
  match List.nth terms 0 with
    | ContextConst index -> context_depth_of_ref ref = index
    | _ -> false

let sko_rule_constrain ref terms refs proof =
  let formula = get_formula proof (List.nth refs 0) in
  let sk_term = List.nth terms 0 in
  if 
    List.for_all 
      (fun v -> var_occurs_free_in_formula v formula && not (var_accurs_free_in_assumptions proof ref v)) 
      (StringSet.elements (free_vars_term sk_term))
    &&
    List.for_all
    (fun v -> var_occurs_in_term v sk_term || var_accurs_free_in_assumptions proof ref v)
    (StringSet.elements (free_vars_formula formula))
  then
    match ref, sk_term with 
      | Ref seq, SkolemConst seq1 -> seq = seq1
      | _ -> false
  else false

let gen_rule_constrain ref terms proof =
  match List.nth terms 0 with 
    | Var v -> not (var_accurs_free_in_assumptions proof ref v)
    | _ -> false

let is_assumption_statement s = 
  match s with
    | AssumptionStmt _ -> true
    | _ -> false

let derive_formula proof rule_label refs terms = 
  rule rule_label (List.map (get_formula proof) refs, terms)

let rec is_valid_conclusion proof r = 
  match get_statement proof r with
    | AssumptionStmt {ref; formula} 
        when ref = r && last_of_ref ref = 0 && asm_formula_match_ref r formula 
        -> true
    | AxiomStmt {ref; label; fofs; terms; formula} 
        when ref = r 
          && formula = (axiom label (fofs, terms))
          && formula_match_ref r formula 
        -> true
    | RuleStmt {ref; label; refs; terms; formula} 
        when ref = r 
          && List.for_all ((>>) ref) refs
          && List.for_all (is_valid_conclusion proof) refs
          && formula_match_ref r formula
        -> (match label with 
            | "CTV" when ctv_rule_constrain r terms -> formula = derive_formula proof label refs terms
            | "SKO" when sko_rule_constrain r terms refs proof -> formula = derive_formula proof label refs terms
            | "GEN" when gen_rule_constrain r terms proof -> formula = derive_formula proof label refs terms
            | "MOD" | "IDN" -> formula = derive_formula proof label refs terms
            | _ -> failwith "invalid proof")
    | BlockStmt{ref; statements; formula} 
        when ref = r 
        && (List.length statements) > 0
        && formula_match_ref r formula
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