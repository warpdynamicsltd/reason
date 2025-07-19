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

and extract_literals (formula : first_order_formula) : literal list =
  match formula with
  | Or (a, b) -> (extract_literals a) @ (extract_literals b)
  | Pred (name, args) -> [Pos (name, args)]
  | Not (Pred (name, args)) -> [Neg (name, args)]
  | _ -> failwith "Expected literal in clause"
 
let to_cnf (formula : first_order_formula) =
  formula
  |> to_nnf                    (* Step 1: Convert to NNF *)
  |> (fun f -> skolemize f []) (* Step 2: Skolemization *)
  |> drop_universals           (* Step 3: Drop universal quantifiers *)
  |> distribute_or             (* Step 4: Distribute OR over AND *)