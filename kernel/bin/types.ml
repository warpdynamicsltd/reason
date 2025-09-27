type reference =
  | Ref of int list

(* Type for terms (constants, variables, function applications) *)
type term =
  | Var of string                                          (* Variables *)
  | Const of string                                        (* Constants *)
  | ContextConst of int                                    (* Conetxt bound const refered by int which means the depth of context *)
  | SkolemConst of int list                                (* Skolem Const refered by int list with the same meaning as in Ref *)
  | Func of string * term list                             (* Function symbols with arguments *)

(* Type for first-order logic formulas *)
type first_order_formula =
  | True                                                   (* Logical constant True *)
  | False                                                  (* Logical constant False *)
  | Pred of string * term list                             (* Predicate with terms as arguments *)
  | Not of first_order_formula                             (* Negation *)
  | And of first_order_formula * first_order_formula       (* Conjunction *)
  | Or of first_order_formula * first_order_formula        (* Disjunction *)
  | Implies of first_order_formula * first_order_formula   (* Implication *)
  | Iff of first_order_formula * first_order_formula       (* Bi-conditional (if and only if) *)
  | Forall of string * first_order_formula                 (* Universal quantifier *)
  | Exists of string * first_order_formula                 (* Existential quantifier *)


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
      statements: statement list;
      formula: first_order_formula
    }


