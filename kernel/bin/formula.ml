(* Type for terms (constants, variables, function applications) *)
type term =
  | Var of string                      (* Variables *)
  | Const of string                    (* Constants *)
  | Func of string * term list         (* Function symbols with arguments *)

(* Type for first-order logic formulas *)
type first_order_formula =
  | True                               (* Logical constant True *)
  | False                              (* Logical constant False *)
  | Pred of string * term list         (* Predicate with terms as arguments *)
  | Not of first_order_formula         (* Negation *)
  | And of first_order_formula * first_order_formula (* Conjunction *)
  | Or of first_order_formula * first_order_formula  (* Disjunction *)
  | Implies of first_order_formula * first_order_formula (* Implication *)
  | Iff of first_order_formula * first_order_formula (* Bi-conditional (if and only if) *)
  | Forall of string * first_order_formula (* Universal quantifier *)
  | Exists of string * first_order_formula (* Existential quantifier *)





