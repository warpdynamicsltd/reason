
type first_order_formula = int;;

type rule_id = 
  | Rule_Mul2
  | Rule_Add2
  | Rule_Add3

let rule = function
  | Rule_Mul2 -> (
        fun ([a; b], k)-> a * b
      )
  | Rule_Add2 -> (fun ([a; b], k) -> a + b)
  | Rule_Add3 -> (fun ([a1; a2; a3], k) -> a1 + a2 + a3);; 


type step =
  | Axiom of first_order_formula
  | Step of (int list * rule_id * first_order_formula)


let conclusion proof_lst i =
  match List.nth proof_lst i with
    | Step(_, _, formula) -> formula
    | Axiom(formula) -> formula


let rec is_proved proof k =
  match List.nth proof k with
    | Axiom formula -> true
    | Step(indecies, rule_id, formula) 
      when
        List.for_all (fun i -> i < k && is_proved proof i) indecies &&
        (rule rule_id)(List.map(conclusion proof) indecies, k) = formula -> true
    | _ -> false;;
    
let is_valid_proof proof = (List.length proof > 0) && (is_proved proof (List.length proof- 1));;


is_valid_proof 
[
  Axiom(1);
  Axiom(2);
  Step([0; 0], Rule_Add2, 2);
  Step([1; 2], Rule_Mul2, 4);
  Step([1; 2; 3], Rule_Add3, 8);
  Step([3; 4], Rule_Add2, 12);
];;

is_valid_proof
[Axiom(1)];;