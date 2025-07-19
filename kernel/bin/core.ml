open Formula

let rec to_nnf (formula : first_order_formula) : first_order_formula =
  match formula with
  | True -> True
  | False -> False
  | Pred (name, args) -> Pred (name, args)

  (* Eliminate implications *)
  | Implies (a, b) -> to_nnf (Or (Not a, b))

  (* Eliminate biconditionals *)
  | Iff (a, b) -> to_nnf (And (Implies (a, b), Implies (b, a)))

  (* Push negations inward *)
  | Not (True) -> False
  | Not (False) -> True
  | Not (Not a) -> to_nnf a  (* Double negation *)
  | Not (And (a, b)) -> to_nnf (Or (Not a, Not b))  (* De Morgan *)
  | Not (Or (a, b)) -> to_nnf (And (Not a, Not b))  (* De Morgan *)
  | Not (Implies (a, b)) -> to_nnf (And (a, Not b))
  | Not (Iff (a, b)) -> to_nnf (Not (And (Implies (a, b), Implies (b, a))))
  | Not (Forall (x, a)) -> to_nnf (Exists (x, Not a))
  | Not (Exists (x, a)) -> to_nnf (Forall (x, Not a))
  | Not (Pred (name, args)) -> Not (Pred (name, args))  (* Already in NNF *)

  (* Recursively process subformulas *)
  | And (a, b) -> And (to_nnf a, to_nnf b)
  | Or (a, b) -> Or (to_nnf a, to_nnf b)
  | Forall (x, a) -> Forall (x, to_nnf a)
  | Exists (x, a) -> Exists (x, to_nnf a)

(* Substitute variable in a term *)
let rec substitute_var_in_term (var : string) (replacement : term) (t : term) : term =
  match t with
  | Var v -> if v = var then replacement else Var v
  | Const c -> Const c
  | Func (f, args) -> Func (f, List.map (substitute_var_in_term var replacement) args)

(* Substitute variable in a formula *)
let rec substitute_var (var : string) (replacement : term) (formula : first_order_formula) : first_order_formula =
  match formula with
  | True -> True
  | False -> False
  | Pred (name, args) -> Pred (name, List.map (substitute_var_in_term var replacement) args)
  | Not f -> Not (substitute_var var replacement f)
  | And (f1, f2) -> And (substitute_var var replacement f1, substitute_var var replacement f2)
  | Or (f1, f2) -> Or (substitute_var var replacement f1, substitute_var var replacement f2)
  | Implies (f1, f2) -> Implies (substitute_var var replacement f1, substitute_var var replacement f2)
  | Iff (f1, f2) -> Iff (substitute_var var replacement f1, substitute_var var replacement f2)
  | Forall (x, f) -> 
      if x = var then Forall (x, f)  (* Variable shadowing - don't substitute *)
      else Forall (x, substitute_var var replacement f)
  | Exists (x, f) -> 
      if x = var then Exists (x, f)  (* Variable shadowing - don't substitute *)
      else Exists (x, substitute_var var replacement f)



(* ∃x.P(x) becomes P(c) where c is a new constant *)
(* ∀x.∃y.P(x,y) becomes ∀x.P(x, f(x)) where f is a new function *)

let rec skolemize (formula : first_order_formula) (universals : string list) : first_order_formula =
  match formula with
  | Exists (x, body) ->
      let skolem_term = 
        if universals = [] then
          Const ("sk_" ^ x)  (* Skolem constant *)
        else
          Func ("sk_" ^ x, List.map (fun v -> Var v) universals)  (* Skolem function *)
      in
      skolemize (substitute_var x skolem_term body) universals
  | Forall (x, body) ->
      Forall (x, skolemize body (x :: universals))
  | And (a, b) -> And (skolemize a universals, skolemize b universals)
  | Or (a, b) -> Or (skolemize a universals, skolemize b universals)
  | _ -> formula


let rec drop_universals (formula : first_order_formula) : first_order_formula =
  match formula with
  | Forall (_, body) -> drop_universals body
  | And (a, b) -> And (drop_universals a, drop_universals b)
  | Or (a, b) -> Or (drop_universals a, drop_universals b)
  | _ -> formula


let rec distribute_or (formula : first_order_formula) : first_order_formula =
  match formula with
  | Or (a, And (b, c)) -> 
      And (distribute_or (Or (a, b)), distribute_or (Or (a, c)))
  | Or (And (a, b), c) -> 
      And (distribute_or (Or (a, c)), distribute_or (Or (b, c)))
  | And (a, b) -> And (distribute_or a, distribute_or b)
  | Or (a, b) -> Or (distribute_or a, distribute_or b)
  | _ -> formula


 (* Clause representation *)
type literal = 
  | Pos of string * term list  (* Positive literal *)
  | Neg of string * term list  (* Negative literal *)

type clause = literal list
type cnf = clause list

let rec extract_literals (formula : first_order_formula) : literal list =
  match formula with
  | Or (a, b) -> (extract_literals a) @ (extract_literals b)
  | Pred (name, args) -> [Pos (name, args)]
  | Not (Pred (name, args)) -> [Neg (name, args)]
  | _ -> failwith "Expected literal in clause"

(* Extract clauses from CNF formula *)
let rec extract_clauses (formula : first_order_formula) : cnf =
  match formula with
  | And (a, b) -> (extract_clauses a) @ (extract_clauses b)
  | Or (_, _) -> [extract_literals formula]
  | Pred (name, args) -> [[Pos (name, args)]]
  | Not (Pred (name, args)) -> [[Neg (name, args)]]
  | True -> []  (* Empty clause set *)
  | False -> [[]]  (* Empty clause (contradiction) *)
  | _ -> failwith "Formula not in proper CNF form"
 
let to_cnf (formula : first_order_formula) =
  formula
  |> to_nnf                    (* Step 1: Convert to NNF *)
  |> (fun f -> skolemize f []) (* Step 2: Skolemization *)
  |> drop_universals           (* Step 3: Drop universal quantifiers *)
  |> distribute_or             (* Step 4: Distribute OR over AND *)




(* ========== HELPER FUNCTIONS ========== *)

(* Check if a variable occurs free in a term *)
let rec occurs_free_in_term (var : string) (t : term) : bool =
  match t with
  | Var v -> v = var
  | Const _ -> false
  | Func (_, args) -> List.exists (occurs_free_in_term var) args

(* Check if a variable occurs free in a formula *)
let rec occurs_free (var : string) (formula : first_order_formula) : bool =
  match formula with
  | True | False -> false
  | Pred (_, args) -> List.exists (occurs_free_in_term var) args
  | Not f -> occurs_free var f
  | And (f1, f2) | Or (f1, f2) | Implies (f1, f2) | Iff (f1, f2) ->
      occurs_free var f1 || occurs_free var f2
  | Forall (x, f) | Exists (x, f) ->
      if x = var then false else occurs_free var f

(* Get all free variables in a formula *)
let free_vars (formula : first_order_formula) : string list =
  let rec free_vars_term (t : term) : string list =
    match t with
    | Var v -> [v]
    | Const _ -> []
    | Func (_, args) -> List.flatten (List.map free_vars_term args)
  in
  let remove_duplicates lst =
    List.fold_left (fun acc x -> if List.mem x acc then acc else x :: acc) [] lst
  in
  let rec aux bounded_vars formula =
    match formula with
    | True | False -> []
    | Pred (_, args) -> 
        List.flatten (List.map free_vars_term args)
        |> List.filter (fun v -> not (List.mem v bounded_vars))
    | Not f -> aux bounded_vars f
    | And (f1, f2) | Or (f1, f2) | Implies (f1, f2) | Iff (f1, f2) ->
        (aux bounded_vars f1) @ (aux bounded_vars f2)
    | Forall (x, f) | Exists (x, f) ->
        aux (x :: bounded_vars) f
  in
  aux [] formula |> remove_duplicates

(* Check if formula is simple (atomic or negated atomic) *)
let is_simple (formula : first_order_formula) : bool =
  match formula with
  | Pred (_, _) | Not (Pred (_, _)) | True | False -> true
  | _ -> false

(* Check if formula is a literal *)
let is_literal (formula : first_order_formula) : bool =
  match formula with
  | Pred (_, _) | Not (Pred (_, _)) -> true
  | _ -> false

(* ========== ADVANCED FORMULA SIMPLIFICATIONS ========== *)

(* Simplify boolean combinations *)
let rec simplify_boolean (formula : first_order_formula) : first_order_formula =
  match formula with
  (* Identity laws *)
  | And (True, f) | And (f, True) -> simplify_boolean f
  | Or (False, f) | Or (f, False) -> simplify_boolean f

  (* Absorption laws *)
  | And (False, _) | And (_, False) -> False
  | Or (True, _) | Or (_, True) -> True

  (* Idempotent laws *)
  | And (f1, f2) when f1 = f2 -> simplify_boolean f1
  | Or (f1, f2) when f1 = f2 -> simplify_boolean f1

  (* Contradiction laws *)
  | And (f1, Not f2) when f1 = f2 -> False
  | And (Not f1, f2) when f1 = f2 -> False
  | Or (f1, Not f2) when f1 = f2 -> True
  | Or (Not f1, f2) when f1 = f2 -> True

  (* Recursive simplification *)
  | And (f1, f2) -> 
      let sf1 = simplify_boolean f1 in
      let sf2 = simplify_boolean f2 in
      if sf1 = f1 && sf2 = f2 then formula
      else simplify_boolean (And (sf1, sf2))
  | Or (f1, f2) ->
      let sf1 = simplify_boolean f1 in
      let sf2 = simplify_boolean f2 in
      if sf1 = f1 && sf2 = f2 then formula
      else simplify_boolean (Or (sf1, sf2))
  | Not f ->
      let sf = simplify_boolean f in
      if sf = f then formula else simplify_boolean (Not sf)
  | _ -> formula

(* ========== QUANTIFIER MINISCOPING ========== *)

(* Move quantifiers as deep as possible into the formula *)
let rec quantifier_miniscoping (formula : first_order_formula) : first_order_formula =
  match formula with
  | Forall (x, And (f1, f2)) ->
      if not (occurs_free x f1) then
        And (f1, quantifier_miniscoping (Forall (x, f2)))
      else if not (occurs_free x f2) then
        And (quantifier_miniscoping (Forall (x, f1)), f2)
      else
        Forall (x, quantifier_miniscoping (And (f1, f2)))

  | Forall (x, Or (f1, f2)) ->
      if not (occurs_free x f1) && not (occurs_free x f2) then
        Or (f1, f2)  (* Remove unused quantifier *)
      else
        Forall (x, quantifier_miniscoping (Or (f1, f2)))

  | Exists (x, Or (f1, f2)) ->
      if not (occurs_free x f1) then
        Or (f1, quantifier_miniscoping (Exists (x, f2)))
      else if not (occurs_free x f2) then
        Or (quantifier_miniscoping (Exists (x, f1)), f2)
      else
        Exists (x, quantifier_miniscoping (Or (f1, f2)))

  | Exists (x, And (f1, f2)) ->
      if not (occurs_free x f1) && not (occurs_free x f2) then
        And (f1, f2)  (* Remove unused quantifier *)
      else
        Exists (x, quantifier_miniscoping (And (f1, f2)))

  (* Remove unused quantifiers *)
  | Forall (x, f) when not (occurs_free x f) -> quantifier_miniscoping f
  | Exists (x, f) when not (occurs_free x f) -> quantifier_miniscoping f

  (* Recursive cases *)
  | And (f1, f2) -> And (quantifier_miniscoping f1, quantifier_miniscoping f2)
  | Or (f1, f2) -> Or (quantifier_miniscoping f1, quantifier_miniscoping f2)
  | Not f -> Not (quantifier_miniscoping f)
  | Forall (x, f) -> Forall (x, quantifier_miniscoping f)
  | Exists (x, f) -> Exists (x, quantifier_miniscoping f)
  | _ -> formula

(* ========== OPTIMIZED EQUIVALENCE HANDLING ========== *)

(* Advanced equivalence elimination with optimizations *)
let rec optimize_equivalences (formula : first_order_formula) : first_order_formula =
  match formula with
  (* Simple equivalences *)
  | Iff (True, f) | Iff (f, True) -> optimize_equivalences f
  | Iff (False, f) | Iff (f, False) -> optimize_equivalences (Not f)

  (* Literal equivalences - more efficient than full expansion *)
  | Iff (f1, f2) when is_literal f1 && is_literal f2 ->
      And (Or (Not f1, f2), Or (f1, Not f2))

  (* Self equivalence *)
  | Iff (f1, f2) when f1 = f2 -> True

  (* Negation equivalences *)
  | Iff (f1, Not f2) | Iff (Not f1, f2) ->
      optimize_equivalences (Not (Iff (f1, f2)))

  (* General case - expand to implications *)
  | Iff (f1, f2) ->
      optimize_equivalences (And (Implies (f1, f2), Implies (f2, f1)))

  (* Recursive cases *)
  | And (f1, f2) -> And (optimize_equivalences f1, optimize_equivalences f2)
  | Or (f1, f2) -> Or (optimize_equivalences f1, optimize_equivalences f2)
  | Implies (f1, f2) -> Implies (optimize_equivalences f1, optimize_equivalences f2)
  | Not f -> Not (optimize_equivalences f)
  | Forall (x, f) -> Forall (x, optimize_equivalences f)
  | Exists (x, f) -> Exists (x, optimize_equivalences f)
  | _ -> formula

(* ========== TERM PREPROCESSING ========== *)

(* Optimize term structure *)
let rec optimize_terms (formula : first_order_formula) : first_order_formula =
  let rec optimize_term (t : term) : term =
    match t with
    | Func (f, args) ->
        let optimized_args = List.map optimize_term args in
        Func (f, optimized_args)
    | _ -> t
  in
  match formula with
  | Pred (name, args) -> Pred (name, List.map optimize_term args)
  | Not f -> Not (optimize_terms f)
  | And (f1, f2) -> And (optimize_terms f1, optimize_terms f2)
  | Or (f1, f2) -> Or (optimize_terms f1, optimize_terms f2)
  | Implies (f1, f2) -> Implies (optimize_terms f1, optimize_terms f2)
  | Iff (f1, f2) -> Iff (optimize_terms f1, optimize_terms f2)
  | Forall (x, f) -> Forall (x, optimize_terms f)
  | Exists (x, f) -> Exists (x, optimize_terms f)
  | _ -> formula

(* ========== PRENEX NORMAL FORM UTILITIES ========== *)

(* Convert to prenex normal form (all quantifiers at the front) *)
let to_prenex (formula : first_order_formula) : first_order_formula =
  let counter = ref 0 in
  let fresh_var prefix =
    incr counter;
    prefix ^ "_" ^ string_of_int !counter
  in

  let rename_var old_var new_var formula =
    substitute_var old_var (Var new_var) formula
  in

  let rec prenex_aux formula =
    match formula with
    | And (Forall (x1, f1), Forall (x2, f2)) ->
        let x1' = fresh_var "X" in
        let x2' = fresh_var "X" in
        Forall (x1', Forall (x2', prenex_aux (And (rename_var x1 x1' f1, rename_var x2 x2' f2))))

    | And (Exists (x1, f1), Exists (x2, f2)) ->
        let x1' = fresh_var "X" in
        let x2' = fresh_var "X" in
        Exists (x1', Exists (x2', prenex_aux (And (rename_var x1 x1' f1, rename_var x2 x2' f2))))

    | And (Forall (x1, f1), f2) ->
        let x1' = fresh_var "X" in
        Forall (x1', prenex_aux (And (rename_var x1 x1' f1, f2)))

    | And (f1, Forall (x2, f2)) ->
        let x2' = fresh_var "X" in
        Forall (x2', prenex_aux (And (f1, rename_var x2 x2' f2)))

    | Or (Exists (x1, f1), Exists (x2, f2)) ->
        let x1' = fresh_var "X" in
        let x2' = fresh_var "X" in
        Exists (x1', Exists (x2', prenex_aux (Or (rename_var x1 x1' f1, rename_var x2 x2' f2))))

    | Or (Forall (x1, f1), Forall (x2, f2)) ->
        let x1' = fresh_var "X" in
        let x2' = fresh_var "X" in
        Forall (x1', Forall (x2', prenex_aux (Or (rename_var x1 x1' f1, rename_var x2 x2' f2))))

    | And (f1, f2) -> And (prenex_aux f1, prenex_aux f2)
    | Or (f1, f2) -> Or (prenex_aux f1, prenex_aux f2)
    | Not f -> Not (prenex_aux f)
    | _ -> formula
  in
  prenex_aux formula

(* ========== ENHANCED NNF WITH OPTIMIZATIONS ========== *)

(* Enhanced NNF with all optimizations *)
let to_ennf (formula : first_order_formula) : first_order_formula =
  let rec ennf_aux formula =
    match formula with
    | True -> True
    | False -> False
    | Pred (name, args) -> Pred (name, args)

    (* Optimized implication elimination *)
    | Implies (False, _) -> True
    | Implies (True, f) -> ennf_aux f
    | Implies (_, True) -> True
    | Implies (f, False) -> ennf_aux (Not f)
    | Implies (f1, f2) when f1 = f2 -> True
    | Implies (f1, Not f2) when f1 = f2 -> ennf_aux (Not f1)
    | Implies (f1, f2) -> ennf_aux (Or (Not f1, f2))

    (* Enhanced negation handling *)
    | Not (True) -> False
    | Not (False) -> True
    | Not (Not f) -> ennf_aux f
    | Not (And (f1, f2)) -> ennf_aux (Or (Not f1, Not f2))
    | Not (Or (f1, f2)) -> ennf_aux (And (Not f1, Not f2))
    | Not (Implies (f1, f2)) -> ennf_aux (And (f1, Not f2))
    | Not (Iff (f1, f2)) -> ennf_aux (Not (And (Implies (f1, f2), Implies (f2, f1))))
    | Not (Forall (x, f)) -> ennf_aux (Exists (x, Not f))
    | Not (Exists (x, f)) -> ennf_aux (Forall (x, Not f))
    | Not (Pred (name, args)) -> Not (Pred (name, args))

    (* Enhanced conjunction/disjunction *)
    | And (f1, f2) ->
        let sf1 = ennf_aux f1 in
        let sf2 = ennf_aux f2 in
        (match sf1, sf2 with
         | True, f | f, True -> f
         | False, _ | _, False -> False
         | _ when sf1 = sf2 -> sf1
         | _ -> And (sf1, sf2))

    | Or (f1, f2) ->
        let sf1 = ennf_aux f1 in
        let sf2 = ennf_aux f2 in
        (match sf1, sf2 with
         | False, f | f, False -> f
         | True, _ | _, True -> True
         | _ when sf1 = sf2 -> sf1
         | _ -> Or (sf1, sf2))

    (* Quantifier handling with miniscoping *)
    | Forall (x, f) ->
        let sf = ennf_aux f in
        if not (occurs_free x sf) then sf
        else Forall (x, sf)

    | Exists (x, f) ->
        let sf = ennf_aux f in
        if not (occurs_free x sf) then sf
        else Exists (x, sf)

    (* Equivalence handled by optimize_equivalences *)
    | Iff (f1, f2) ->
        ennf_aux (optimize_equivalences (Iff (f1, f2)))
  in

  (* Apply all ENNF transformations in sequence *)
  formula
  |> optimize_terms              (* Step 1: Term optimization *)
  |> optimize_equivalences       (* Step 2: Advanced equivalence handling *)
  |> ennf_aux                   (* Step 3: Enhanced NNF conversion *)
  |> quantifier_miniscoping     (* Step 4: Quantifier miniscoping *)
  |> simplify_boolean           (* Step 5: Boolean simplification *)

(* ========== ADDITIONAL ENNF UTILITIES ========== *)

(* Check if formula is in ENNF *)
let rec is_ennf (formula : first_order_formula) : bool =
  match formula with
  | True | False | Pred (_, _) -> true
  | Not (Pred (_, _)) -> true
  | Not _ -> false  (* Negation only before predicates *)
  | And (f1, f2) | Or (f1, f2) -> is_ennf f1 && is_ennf f2
  | Forall (_, f) | Exists (_, f) -> is_ennf f
  | Implies (_, _) | Iff (_, _) -> false  (* Should be eliminated *)

(* ========== MAIN ENNF FUNCTION ========== *)

(* Complete ENNF transformation *)
let full_ennf (formula : first_order_formula) : first_order_formula =
  let result = to_ennf formula in
  if is_ennf result then result
  else failwith "ENNF transformation failed to produce valid ENNF"
