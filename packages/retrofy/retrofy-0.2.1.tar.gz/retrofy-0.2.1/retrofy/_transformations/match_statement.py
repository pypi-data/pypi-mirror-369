from __future__ import annotations

from typing import List, Optional, Tuple, Union

import libcst as cst

from .import_utils import ImportManager


class VariableSubstituter(cst.CSTTransformer):
    """Substitute variable names with expressions in CST nodes."""

    def __init__(self, substitutions: dict[str, cst.BaseExpression]):
        super().__init__()
        self.substitutions = substitutions

    def leave_Name(
        self,
        original_node: cst.Name,
        updated_node: cst.Name,
    ) -> cst.BaseExpression:
        """Replace variable names with their substitutions."""
        if updated_node.value in self.substitutions:
            return self.substitutions[updated_node.value]
        return updated_node


class MatchStatementTransformer(cst.CSTTransformer):
    """
    Transform match statements to compatible if/elif/else syntax.

    This implementation handles basic patterns but cannot perfectly translate
    all match statement semantics to pre-Python 3.10 syntax.

    Supported Transformations:

    1. Literal patterns:
       match x: case 42: ... -> if x == 42: ...

    2. Simple variable binding:
       match x: case y: ... -> y = x; ...

    3. Wildcard patterns:
       match x: case _: ... -> else: ...

    4. Simple OR patterns (literals only):
       match x: case 1 | 2: ... -> if x in (1, 2): ...

    Limitations:
    - Complex OR patterns with different variable bindings
    - Nested destructuring patterns become verbose
    - Guard clauses lose some semantic guarantees
    - Star patterns require complex slicing logic
    - Class patterns require explicit isinstance checks
    """

    def __init__(self):
        super().__init__()
        self.import_manager = ImportManager()

    def _create_optimized_isinstance_check(
        self,
        subject: cst.BaseExpression,
        positive_type: cst.BaseExpression,
        negative_types: list[cst.BaseExpression],
    ) -> cst.BaseExpression:
        """Create an optimized isinstance check using tuple for negative types."""
        positive_check = cst.Call(
            cst.Name("isinstance"),
            [cst.Arg(subject), cst.Arg(positive_type)],
        )

        if not negative_types:
            return positive_check

        if len(negative_types) == 1:
            negative_check = cst.Call(
                cst.Name("isinstance"),
                [cst.Arg(subject), cst.Arg(negative_types[0])],
            )
        else:
            # Use tuple for multiple types
            tuple_elements = [cst.Element(typ) for typ in negative_types]
            tuple_expr = cst.Tuple(tuple_elements)
            negative_check = cst.Call(
                cst.Name("isinstance"),
                [cst.Arg(subject), cst.Arg(tuple_expr)],
            )

        return cst.BooleanOperation(
            left=positive_check,
            operator=cst.And(),
            right=cst.UnaryOperation(cst.Not(), negative_check),
        )

    def leave_Match(
        self,
        original_node: cst.Match,
        updated_node: cst.Match,
    ) -> Union[cst.If, cst.SimpleStatementLine, cst.IndentedBlock]:
        """Transform a match statement into if/elif/else chains."""
        subject = updated_node.subject
        cases = updated_node.cases

        if not cases:
            # Empty match - just return the subject as a statement
            return cst.SimpleStatementLine([cst.Expr(subject)])

        # Expand OR patterns into separate cases (except for simple literal OR patterns)
        expanded_cases = []
        for case in cases:
            if isinstance(case.pattern, cst.MatchOr):
                # Check if all patterns in the OR are simple literals
                patterns = [element.pattern for element in case.pattern.patterns]
                all_literals = all(
                    isinstance(pat, (cst.MatchValue, cst.MatchSingleton))
                    for pat in patterns
                )

                if all_literals:
                    # Keep simple literal OR patterns as-is for 'in' operator optimization
                    expanded_cases.append(case)
                else:
                    # Expand complex OR pattern into separate cases
                    for pattern in patterns:
                        expanded_case = case.with_changes(pattern=pattern)
                        expanded_cases.append(expanded_case)
            else:
                expanded_cases.append(case)

        # We'll handle __match_args__ validation directly in the if/elif building

        # Special case: single case with no conditions (just variable binding)
        if len(expanded_cases) == 1:
            case_stmt = self._build_case_condition(subject, expanded_cases[0])
            if isinstance(case_stmt, cst.Else):
                # Extract all statements from the else block and return as a flat sequence
                if isinstance(case_stmt.body, cst.IndentedBlock):
                    return cst.FlattenSentinel(case_stmt.body.body)

        # Build the if/elif/else chain with special handling for class patterns
        result = None

        for case in reversed(expanded_cases):
            # Check if this case needs a __match_args__ error check
            if isinstance(case.pattern, cst.MatchClass) and case.pattern.patterns:
                # Build the normal case statement first
                case_stmt = self._build_case_condition(subject, case)

                # Create the error check statement
                error_stmt = self._build_match_args_error_check(subject, case.pattern)

                # Insert the error check before the normal case
                if result is None:
                    # This is the last case, so chain error -> normal case
                    if isinstance(case_stmt, cst.If):
                        result = error_stmt.with_changes(orelse=case_stmt)
                    else:
                        # case_stmt is Else
                        result = error_stmt.with_changes(orelse=case_stmt)
                else:
                    # Chain: error -> normal case -> rest
                    if isinstance(case_stmt, cst.If):
                        chained_case = case_stmt.with_changes(orelse=result)
                        result = error_stmt.with_changes(orelse=chained_case)
                    else:
                        # case_stmt is Else - this shouldn't happen for class patterns
                        result = error_stmt.with_changes(orelse=result)
            else:
                # Normal case handling
                case_stmt = self._build_case_condition(subject, case)

                if result is None:
                    result = case_stmt
                else:
                    if isinstance(case_stmt, cst.If):
                        result = case_stmt.with_changes(orelse=result)
                    elif isinstance(case_stmt, cst.Else):
                        result = case_stmt

        return result or cst.SimpleStatementLine([cst.Expr(subject)])

    def leave_Module(
        self,
        original_node: cst.Module,
        updated_node: cst.Module,
    ) -> cst.Module:
        """Apply import management."""
        return self.import_manager.apply_imports(updated_node)

    def _build_case_condition(
        self,
        subject: cst.BaseExpression,
        case: cst.MatchCase,
    ) -> Union[cst.If, cst.Else]:
        """Build the condition and body for a single case."""
        pattern = case.pattern
        guard = case.guard
        body = case.body

        # Handle wildcard pattern
        if isinstance(pattern, cst.MatchAs) and pattern.name is None:
            # case _: -> else:
            return cst.Else(body=body)

        # Generate condition and variable assignments
        condition, assignments = self._pattern_to_condition(subject, pattern)

        # Add guard condition if present
        if guard:
            # Always substitute variables in guard to avoid undefined variable errors
            substituted_guard = self._substitute_variables_in_guard(
                guard,
                assignments,
                subject,
            )

            if condition:
                condition = cst.BooleanOperation(
                    left=condition,
                    operator=cst.And(),
                    right=substituted_guard,
                )
            else:
                condition = substituted_guard

        # If no condition (e.g., simple variable binding), treat as else
        if condition is None:
            combined_body = self._combine_assignments_and_body(assignments, body)
            return cst.Else(body=combined_body)

        # Build the if statement
        combined_body = self._combine_assignments_and_body(assignments, body)
        return cst.If(test=condition, body=combined_body)

    def _pattern_to_condition(
        self,
        subject: cst.BaseExpression,
        pattern: cst.BaseMatchPattern,
    ) -> Tuple[Optional[cst.BaseExpression], List[cst.BaseSmallStatement]]:
        """Convert a pattern to a condition and list of variable assignments."""

        if isinstance(pattern, cst.MatchValue):
            # Literal pattern: case 42: -> if subject == 42:
            condition = cst.Comparison(
                left=subject,
                comparisons=[
                    cst.ComparisonTarget(
                        operator=cst.Equal(),
                        comparator=pattern.value,
                    ),
                ],
            )
            return condition, []

        elif isinstance(pattern, cst.MatchSingleton):
            # Singleton pattern: case True/False/None: -> if subject is True:
            # Use 'is' for singletons to match Python's match statement semantics
            condition = cst.Comparison(
                left=subject,
                comparisons=[
                    cst.ComparisonTarget(
                        operator=cst.Is(),
                        comparator=pattern.value,
                    ),
                ],
            )
            return condition, []

        elif isinstance(pattern, cst.MatchAs):
            if pattern.pattern is None:
                # Simple variable binding: case x: -> x = subject
                if pattern.name:
                    assignment = cst.Assign([cst.AssignTarget(pattern.name)], subject)
                    return None, [assignment]
                else:
                    # case _: (wildcard)
                    return None, []
            else:
                # Pattern with as binding: case (x, y) as point:
                inner_condition, inner_assignments = self._pattern_to_condition(
                    subject,
                    pattern.pattern,
                )
                if pattern.name:
                    capture_assignment = cst.Assign(
                        [cst.AssignTarget(pattern.name)],
                        subject,
                    )
                    return inner_condition, [capture_assignment] + inner_assignments
                return inner_condition, inner_assignments

        elif isinstance(pattern, cst.MatchOr):
            patterns = [element.pattern for element in pattern.patterns]

            # Process patterns in order to preserve short-circuit evaluation
            conditions = []
            all_literals = True
            all_types = True

            for pat in patterns:
                if isinstance(pat, (cst.MatchValue, cst.MatchSingleton)):
                    # Literal pattern: case 0: -> value == 0
                    all_types = False
                    equality_condition = cst.Comparison(
                        left=subject,
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=pat.value,
                            ),
                        ],
                    )
                    conditions.append(equality_condition)
                elif (
                    isinstance(pat, cst.MatchClass)
                    and not pat.patterns
                    and not pat.kwds
                ):
                    # Type pattern: case int(): -> isinstance(value, int)
                    all_literals = False
                    isinstance_condition = cst.Call(
                        cst.Name("isinstance"),
                        [cst.Arg(subject), cst.Arg(pat.cls)],
                    )
                    conditions.append(isinstance_condition)
                else:
                    raise NotImplementedError(
                        "Complex OR patterns should be expanded into separate cases",
                    )

            # Optimize for pure literal patterns: case 1 | 2 | 3: -> if subject in (1, 2, 3):
            if all_literals and len(conditions) > 1:
                literals = []
                for pat in patterns:
                    if isinstance(pat, (cst.MatchValue, cst.MatchSingleton)):
                        literals.append(pat.value)

                tuple_elements = [cst.Element(lit) for lit in literals]
                tuple_expr = cst.Tuple(tuple_elements)
                condition = cst.Comparison(
                    left=subject,
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.In(),
                            comparator=tuple_expr,
                        ),
                    ],
                )
                return condition, []

            # Optimize for pure type patterns: case int() | float(): -> isinstance(subject, (int, float))
            elif all_types and len(conditions) > 1:
                types = []
                for pat in patterns:
                    if (
                        isinstance(pat, cst.MatchClass)
                        and not pat.patterns
                        and not pat.kwds
                    ):
                        types.append(pat.cls)

                tuple_elements = [cst.Element(typ) for typ in types]
                tuple_expr = cst.Tuple(tuple_elements)
                condition = cst.Call(
                    cst.Name("isinstance"),
                    [cst.Arg(subject), cst.Arg(tuple_expr)],
                )
                return condition, []

            # For mixed patterns or single patterns, combine conditions with OR in order
            if len(conditions) == 1:
                condition = conditions[0]
            else:
                condition = conditions[0]
                for cond in conditions[1:]:
                    condition = cst.BooleanOperation(
                        left=condition,
                        operator=cst.Or(),
                        right=cond,
                    )

            return condition, []

        elif isinstance(pattern, (cst.MatchSequence, cst.MatchTuple)):
            # Sequence/tuple pattern: case [x, y] or case (x, y): -> if len(subject) == 2: x, y = subject
            elements = pattern.patterns

            # Convert MatchSequenceElement to the actual pattern
            actual_elements = []
            for elem in elements:
                if isinstance(elem, cst.MatchSequenceElement):
                    actual_elements.append(elem.value)
                else:
                    actual_elements.append(elem)

            if not actual_elements:
                # Empty sequence: case [] or case (): -> if isinstance(subject, collections.abc.Sequence) and not isinstance(subject, (str, collections.abc.Mapping)) and len(subject) == 0:
                self.import_manager.require_import("collections.abc")
                isinstance_check = self._create_optimized_isinstance_check(
                    subject,
                    cst.Attribute(
                        cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                        cst.Name("Sequence"),
                    ),
                    [
                        cst.Name("str"),
                        cst.Attribute(
                            cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                            cst.Name("Mapping"),
                        ),
                    ],
                )
                length_check = cst.Comparison(
                    left=cst.Call(cst.Name("len"), [cst.Arg(subject)]),
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.Equal(),
                            comparator=cst.Integer("0"),
                        ),
                    ],
                )
                condition = cst.BooleanOperation(
                    left=isinstance_check,
                    operator=cst.And(),
                    right=length_check,
                )
                return condition, []

            # Check if all elements are literals - if so, generate direct comparison
            if all(
                isinstance(elem, (cst.MatchValue, cst.MatchSingleton))
                for elem in actual_elements
            ):
                # Literal tuple/sequence: case (0, 0): -> if subject == (0, 0):
                literal_elements = []
                for elem in actual_elements:
                    literal_elements.append(cst.Element(elem.value))

                if isinstance(pattern, cst.MatchTuple):
                    literal_tuple = cst.Tuple(literal_elements)
                else:
                    literal_tuple = cst.List(literal_elements)

                condition = cst.Comparison(
                    left=subject,
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.Equal(),
                            comparator=literal_tuple,
                        ),
                    ],
                )
                return condition, []

            # Check for star patterns
            star_count = sum(
                1 for elem in actual_elements if isinstance(elem, cst.MatchStar)
            )
            if star_count > 1:
                # Multiple star patterns - invalid
                return None, []

            if star_count == 1:
                # Has star pattern: case [x, *rest, y]: -> complex slicing logic
                return self._handle_star_pattern(subject, actual_elements)

            # Check if all elements are simple variable bindings
            all_variables = all(
                isinstance(elem, cst.MatchAs) and elem.pattern is None and elem.name
                for elem in actual_elements
            )

            if all_variables:
                # All variables: case (x, y): -> if isinstance(subject, collections.abc.Sequence) and not isinstance(subject, (str, collections.abc.Mapping)) and len(subject) == 2: x, y = subject
                self.import_manager.require_import("collections.abc")

                isinstance_check = self._create_optimized_isinstance_check(
                    subject,
                    cst.Attribute(
                        cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                        cst.Name("Sequence"),
                    ),
                    [
                        cst.Name("str"),
                        cst.Attribute(
                            cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                            cst.Name("Mapping"),
                        ),
                    ],
                )

                length_check = cst.Comparison(
                    left=cst.Call(cst.Name("len"), [cst.Arg(subject)]),
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.Equal(),
                            comparator=cst.Integer(str(len(actual_elements))),
                        ),
                    ],
                )

                combined_check = cst.BooleanOperation(
                    left=isinstance_check,
                    operator=cst.And(),
                    right=length_check,
                )

                # Create tuple unpacking assignment
                target_names = [elem.name for elem in actual_elements]
                if len(target_names) == 1:
                    # Single element: x = point[0]
                    assignment = cst.Assign(
                        [cst.AssignTarget(target_names[0])],
                        cst.Subscript(
                            subject,
                            [cst.SubscriptElement(cst.Integer("0"))],
                        ),
                    )
                else:
                    # Multiple elements: x, y = point
                    target_tuple = cst.Tuple(
                        [cst.Element(name) for name in target_names],
                        lpar=[],
                        rpar=[],
                    )
                    assignment = cst.Assign([cst.AssignTarget(target_tuple)], subject)

                return combined_check, [assignment]

            # Mixed pattern: some literals, some variables
            conditions = []
            assignments = []

            # isinstance check - match any Sequence except strings and mappings
            self.import_manager.require_import("collections.abc")
            isinstance_check = self._create_optimized_isinstance_check(
                subject,
                cst.Attribute(
                    cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                    cst.Name("Sequence"),
                ),
                [
                    cst.Name("str"),
                    cst.Attribute(
                        cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                        cst.Name("Mapping"),
                    ),
                ],
            )
            conditions.append(isinstance_check)

            # Length check
            length_check = cst.Comparison(
                left=cst.Call(cst.Name("len"), [cst.Arg(subject)]),
                comparisons=[
                    cst.ComparisonTarget(
                        operator=cst.Equal(),
                        comparator=cst.Integer(str(len(actual_elements))),
                    ),
                ],
            )
            conditions.append(length_check)

            # Element checks and assignments
            for i, elem in enumerate(actual_elements):
                subscript = cst.Subscript(
                    subject,
                    [cst.SubscriptElement(cst.Integer(str(i)))],
                )

                if isinstance(elem, (cst.MatchValue, cst.MatchSingleton)):
                    # Literal check: point[0] == 0
                    elem_check = cst.Comparison(
                        left=subscript,
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=elem.value,
                            ),
                        ],
                    )
                    conditions.append(elem_check)
                elif (
                    isinstance(elem, cst.MatchAs) and elem.pattern is None and elem.name
                ):
                    # Variable binding: x = point[0]
                    assignment = cst.Assign([cst.AssignTarget(elem.name)], subscript)
                    assignments.append(assignment)
                else:
                    # Complex nested pattern - recursively process it
                    elem_condition, elem_assignments = self._pattern_to_condition(
                        subscript,
                        elem,
                    )
                    if elem_condition:
                        conditions.append(elem_condition)
                    assignments.extend(elem_assignments)

            # Combine all conditions
            if len(conditions) == 1:
                combined_condition = conditions[0]
            else:
                combined_condition = conditions[0]
                for cond in conditions[1:]:
                    combined_condition = cst.BooleanOperation(
                        left=combined_condition,
                        operator=cst.And(),
                        right=cond,
                    )

            return combined_condition, assignments

        elif isinstance(pattern, cst.MatchMapping):
            # Dictionary pattern: case {"key": value}: -> isinstance and key checks
            return self._handle_mapping_pattern(subject, pattern)

        elif isinstance(pattern, cst.MatchClass):
            # Class pattern: case Point(x=x, y=y): -> isinstance check + attribute access
            return self._handle_class_pattern(subject, pattern)

        # Fallback for unsupported patterns
        return None, []

    def _handle_star_pattern(
        self,
        subject: cst.BaseExpression,
        elements: List[cst.BaseMatchPattern],
    ) -> Tuple[Optional[cst.BaseExpression], List[cst.BaseSmallStatement]]:
        """Handle sequence patterns with star expressions."""
        star_index = None
        for i, elem in enumerate(elements):
            if isinstance(elem, cst.MatchStar):
                star_index = i
                break

        if star_index is None:
            return None, []

        # Calculate minimum length requirement
        min_length = len(elements) - 1  # All elements except the star

        # Add isinstance check for Sequence (excluding str and Mapping)
        self.import_manager.require_import("collections.abc")
        isinstance_check = self._create_optimized_isinstance_check(
            subject,
            cst.Attribute(
                cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                cst.Name("Sequence"),
            ),
            [
                cst.Name("str"),
                cst.Attribute(
                    cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                    cst.Name("Mapping"),
                ),
            ],
        )

        length_check = cst.Comparison(
            left=cst.Call(cst.Name("len"), [cst.Arg(subject)]),
            comparisons=[
                cst.ComparisonTarget(
                    operator=cst.GreaterThanEqual(),
                    comparator=cst.Integer(str(min_length)),
                ),
            ],
        )

        # Combine isinstance and length checks
        combined_check = cst.BooleanOperation(
            left=isinstance_check,
            operator=cst.And(),
            right=length_check,
        )

        # Note: Literal pattern checks for elements before star are now handled
        # by the recursive pattern processing below to avoid duplication

        assignments = []

        # Handle elements before star
        for i in range(star_index):
            elem = elements[i]
            subscript = cst.Subscript(
                subject,
                [cst.SubscriptElement(cst.Integer(str(i)))],
            )

            if isinstance(elem, cst.MatchAs) and elem.pattern is None and elem.name:
                # Simple variable binding: x = subject[i]
                assignment = cst.Assign([cst.AssignTarget(elem.name)], subscript)
                assignments.append(assignment)
            else:
                # Complex nested pattern - recursively process it
                elem_condition, elem_assignments = self._pattern_to_condition(
                    subscript,
                    elem,
                )
                if elem_condition:
                    # Combine with the existing combined_check
                    combined_check = cst.BooleanOperation(
                        left=combined_check,
                        operator=cst.And(),
                        right=elem_condition,
                    )
                assignments.extend(elem_assignments)

        # Assign star pattern
        star_elem = elements[star_index]
        if isinstance(star_elem, cst.MatchStar) and star_elem.name:
            elements_after = len(elements) - star_index - 1
            if elements_after == 0:
                # case [*rest]: -> rest = list(subject[star_index:])
                slice_expr = cst.Subscript(
                    subject,
                    [
                        cst.SubscriptElement(
                            slice=cst.Slice(
                                lower=cst.Integer(str(star_index)),
                                upper=None,
                            ),
                        ),
                    ],
                )
            else:
                # case [x, *middle, y]: -> middle = list(subject[1:-1])
                slice_expr = cst.Subscript(
                    subject,
                    [
                        cst.SubscriptElement(
                            slice=cst.Slice(
                                lower=cst.Integer(str(star_index)),
                                upper=cst.UnaryOperation(
                                    cst.Minus(),
                                    cst.Integer(str(elements_after)),
                                ),
                            ),
                        ),
                    ],
                )
            # Wrap slice in list() to match Python 3.11+ behavior
            tuple_expr = cst.Call(
                cst.Name("list"),
                [cst.Arg(slice_expr)],
            )
            assignment = cst.Assign([cst.AssignTarget(star_elem.name)], tuple_expr)
            assignments.append(assignment)

        # Handle elements after star
        elements_after_star = len(elements) - star_index - 1
        for i in range(elements_after_star):
            elem = elements[star_index + 1 + i]
            # Use negative indexing for elements after star
            negative_index = elements_after_star - i
            subscript = cst.Subscript(
                subject,
                [
                    cst.SubscriptElement(
                        cst.UnaryOperation(
                            cst.Minus(),
                            cst.Integer(str(negative_index)),
                        ),
                    ),
                ],
            )

            if isinstance(elem, cst.MatchAs) and elem.pattern is None and elem.name:
                # Simple variable binding: x = subject[-i]
                assignment = cst.Assign([cst.AssignTarget(elem.name)], subscript)
                assignments.append(assignment)
            else:
                # Complex nested pattern - recursively process it
                elem_condition, elem_assignments = self._pattern_to_condition(
                    subscript,
                    elem,
                )
                if elem_condition:
                    # Combine with the existing combined_check
                    combined_check = cst.BooleanOperation(
                        left=combined_check,
                        operator=cst.And(),
                        right=elem_condition,
                    )
                assignments.extend(elem_assignments)

        return combined_check, assignments

    def _handle_mapping_pattern(
        self,
        subject: cst.BaseExpression,
        pattern: cst.MatchMapping,
    ) -> Tuple[Optional[cst.BaseExpression], List[cst.BaseSmallStatement]]:
        """Handle dictionary/mapping patterns."""
        conditions = []
        assignments = []

        # isinstance check - match any Mapping per PEP-622
        self.import_manager.require_import("collections.abc")
        isinstance_check = cst.Call(
            cst.Name("isinstance"),
            [
                cst.Arg(subject),
                cst.Arg(
                    cst.Attribute(
                        cst.Attribute(cst.Name("collections"), cst.Name("abc")),
                        cst.Name("Mapping"),
                    ),
                ),
            ],
        )
        conditions.append(isinstance_check)

        # If this is an empty mapping pattern ({}), add length check
        if not pattern.elements:
            length_check = cst.Comparison(
                left=cst.Call(cst.Name("len"), [cst.Arg(subject)]),
                comparisons=[
                    cst.ComparisonTarget(
                        operator=cst.Equal(),
                        comparator=cst.Integer("0"),
                    ),
                ],
            )
            conditions.append(length_check)

        # Collect explicit keys for rest pattern handling
        explicit_keys = []

        # Check each key-value pair
        for element in pattern.elements:
            if isinstance(element, cst.MatchMappingElement):
                key = element.key
                value_pattern = element.pattern

                # Store explicit keys for rest pattern
                if isinstance(key, cst.SimpleString):
                    explicit_keys.append(key)

                # Check key exists
                key_check = cst.Comparison(
                    left=key,
                    comparisons=[
                        cst.ComparisonTarget(
                            operator=cst.In(),
                            comparator=subject,
                        ),
                    ],
                )
                conditions.append(key_check)

                # If it's a literal value, check equality
                if isinstance(value_pattern, cst.MatchValue):
                    value_check = cst.Comparison(
                        left=cst.Subscript(subject, [cst.SubscriptElement(key)]),
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=value_pattern.value,
                            ),
                        ],
                    )
                    conditions.append(value_check)
                elif (
                    isinstance(value_pattern, cst.MatchAs)
                    and value_pattern.pattern is None
                    and value_pattern.name
                ):
                    # Variable binding
                    assignment = cst.Assign(
                        [cst.AssignTarget(value_pattern.name)],
                        cst.Subscript(subject, [cst.SubscriptElement(key)]),
                    )
                    assignments.append(assignment)
                else:
                    # Nested pattern - recursively process it
                    nested_subject = cst.Subscript(subject, [cst.SubscriptElement(key)])
                    nested_condition, nested_assignments = self._pattern_to_condition(
                        nested_subject,
                        value_pattern,
                    )
                    if nested_condition:
                        conditions.append(nested_condition)
                    assignments.extend(nested_assignments)

        # Handle **rest pattern if present
        if pattern.rest and isinstance(pattern.rest, cst.Name):
            # Create a dictionary comprehension to exclude explicit keys
            # rest = {k: v for k, v in subject.items() if k not in {"explicit", "keys"}}

            # Create set of explicit keys for exclusion
            if explicit_keys:
                # Create tuple of explicit keys: ("name", "version", ...)
                explicit_key_elements = [cst.Element(key) for key in explicit_keys]
                explicit_key_set = cst.Set(explicit_key_elements)
            else:
                # Empty set if no explicit keys
                explicit_key_set = cst.Call(cst.Name("set"), [])

            # Create dictionary comprehension: {k: v for k, v in subject.items() if k not in explicit_keys}
            dict_comp = cst.DictComp(
                key=cst.Name("k"),
                value=cst.Name("v"),
                for_in=cst.CompFor(
                    target=cst.Tuple(
                        [cst.Element(cst.Name("k")), cst.Element(cst.Name("v"))],
                    ),
                    iter=cst.Call(
                        cst.Attribute(subject, cst.Name("items")),
                        [],
                    ),
                    ifs=[
                        cst.CompIf(
                            test=cst.Comparison(
                                left=cst.Name("k"),
                                comparisons=[
                                    cst.ComparisonTarget(
                                        operator=cst.NotIn(),
                                        comparator=explicit_key_set,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )

            # Assign the rest dictionary
            rest_assignment = cst.Assign(
                [cst.AssignTarget(pattern.rest)],
                dict_comp,
            )
            assignments.append(rest_assignment)

        # Combine all conditions
        if conditions:
            combined_condition = conditions[0]
            for cond in conditions[1:]:
                combined_condition = cst.BooleanOperation(
                    left=combined_condition,
                    operator=cst.And(),
                    right=cond,
                )
            return combined_condition, assignments

        return None, assignments

    def _handle_class_pattern(
        self,
        subject: cst.BaseExpression,
        pattern: cst.MatchClass,
    ) -> Tuple[Optional[cst.BaseExpression], List[cst.BaseSmallStatement]]:
        """Handle class patterns with isinstance checks."""
        conditions = []
        assignments = []

        # isinstance check
        isinstance_check = cst.Call(
            cst.Name("isinstance"),
            [cst.Arg(subject), cst.Arg(pattern.cls)],
        )
        conditions.append(isinstance_check)

        # For positional patterns, validation is now handled in a separate error case
        # So we can process patterns normally here

        # Handle positional patterns first
        for i, element in enumerate(pattern.patterns):
            if isinstance(element, cst.MatchSequenceElement):
                # Positional pattern: Point(x, 0)
                # Use __match_args__ to get the correct attribute name
                value_pattern = element.value

                # Access the attribute name from __match_args__[i]
                match_args_attr = cst.Attribute(pattern.cls, cst.Name("__match_args__"))
                attr_name_expr = cst.Subscript(
                    match_args_attr,
                    [cst.SubscriptElement(cst.Integer(str(i)))],
                )

                # Get the attribute using getattr(subject, __match_args__[i])
                attr_access = cst.Call(
                    cst.Name("getattr"),
                    [cst.Arg(subject), cst.Arg(attr_name_expr)],
                )

                if isinstance(value_pattern, (cst.MatchValue, cst.MatchSingleton)):
                    # Check attribute value
                    attr_check = cst.Comparison(
                        left=attr_access,
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=value_pattern.value,
                            ),
                        ],
                    )
                    conditions.append(attr_check)
                elif (
                    isinstance(value_pattern, cst.MatchAs)
                    and value_pattern.pattern is None
                    and value_pattern.name
                ):
                    # Bind attribute to variable
                    assignment = cst.Assign(
                        [cst.AssignTarget(value_pattern.name)],
                        attr_access,
                    )
                    assignments.append(assignment)
                else:
                    # Complex nested pattern - recursively process it
                    nested_condition, nested_assignments = self._pattern_to_condition(
                        attr_access,
                        value_pattern,
                    )
                    if nested_condition:
                        conditions.append(nested_condition)
                    assignments.extend(nested_assignments)

        # Handle keyword patterns
        for element in pattern.kwds:
            if isinstance(element, cst.MatchKeywordElement):
                # Keyword pattern: Point(x=value)
                attr_name = (
                    element.key
                )  # Note: it's 'key' not 'keyword' for MatchKeywordElement
                value_pattern = element.pattern

                attr_access = cst.Attribute(subject, attr_name)

                if isinstance(value_pattern, (cst.MatchValue, cst.MatchSingleton)):
                    # Check attribute value
                    attr_check = cst.Comparison(
                        left=attr_access,
                        comparisons=[
                            cst.ComparisonTarget(
                                operator=cst.Equal(),
                                comparator=value_pattern.value,
                            ),
                        ],
                    )
                    conditions.append(attr_check)
                elif (
                    isinstance(value_pattern, cst.MatchAs)
                    and value_pattern.pattern is None
                    and value_pattern.name
                ):
                    # Bind attribute to variable
                    assignment = cst.Assign(
                        [cst.AssignTarget(value_pattern.name)],
                        attr_access,
                    )
                    assignments.append(assignment)
                else:
                    # Complex nested pattern - recursively process it
                    nested_condition, nested_assignments = self._pattern_to_condition(
                        attr_access,
                        value_pattern,
                    )
                    if nested_condition:
                        conditions.append(nested_condition)
                    assignments.extend(nested_assignments)

        # Combine conditions
        if conditions:
            combined_condition = conditions[0]
            for cond in conditions[1:]:
                combined_condition = cst.BooleanOperation(
                    left=combined_condition,
                    operator=cst.And(),
                    right=cond,
                )

            return combined_condition, assignments

        return None, assignments

    def _substitute_variables_in_guard(
        self,
        guard: cst.BaseExpression,
        assignments: List[cst.BaseSmallStatement],
        subject: cst.BaseExpression,
    ) -> cst.BaseExpression:
        """
        Substitute variables from assignments with the subject in guard conditions.

        For example, if we have:
        - guard: y > 0
        - assignments: [y = x]
        - subject: x

        Then substitute y with x in the guard to get: x > 0
        """
        if not assignments:
            return guard

        # Create a mapping of variable names to their assigned values
        var_substitutions = {}
        for assignment in assignments:
            if isinstance(assignment, cst.Assign):
                for target in assignment.targets:
                    if isinstance(target.target, cst.Name):
                        # For star pattern variables assigned as list(slice), use just the slice in guards
                        if (
                            isinstance(assignment.value, cst.Call)
                            and isinstance(assignment.value.func, cst.Name)
                            and assignment.value.func.value == "list"
                            and len(assignment.value.args) == 1
                        ):
                            # Use the slice expression directly for guard conditions
                            var_substitutions[target.target.value] = (
                                assignment.value.args[0].value
                            )
                        else:
                            # Use the assignment value for other variables
                            var_substitutions[target.target.value] = assignment.value
                    elif isinstance(target.target, cst.Tuple):
                        # Handle tuple unpacking: x, y = expr
                        # Substitute each variable with expr[index]
                        for i, element in enumerate(target.target.elements):
                            if isinstance(element.value, cst.Name):
                                subscript = cst.Subscript(
                                    assignment.value,
                                    [cst.SubscriptElement(cst.Integer(str(i)))],
                                )
                                var_substitutions[element.value.value] = subscript

        # Use a transformer to substitute variables
        substituter = VariableSubstituter(var_substitutions)
        return guard.visit(substituter)

    def _combine_assignments_and_body(
        self,
        assignments: List[cst.BaseSmallStatement],
        body: cst.BaseSuite,
    ) -> cst.BaseSuite:
        """Combine variable assignments with the case body."""
        if not assignments:
            return body

        if isinstance(body, cst.SimpleStatementSuite):
            # Combine with simple statements
            new_stmts = assignments + body.body
            return cst.SimpleStatementSuite(new_stmts)
        else:
            # Insert assignments at the beginning of the block
            assignment_lines = [cst.SimpleStatementLine([stmt]) for stmt in assignments]
            if hasattr(body, "body"):
                new_body = list(assignment_lines) + list(body.body)
                return body.with_changes(body=new_body)
            else:
                return cst.IndentedBlock(assignment_lines)

    def _build_match_args_error_check(
        self,
        subject: cst.BaseExpression,
        pattern: cst.MatchClass,
    ) -> cst.If:
        """Build an if statement that checks for __match_args__ errors."""
        num_positional = len(pattern.patterns)
        cls_name = getattr(pattern.cls, "value", "UnknownClass")

        # Create condition: isinstance(subject, cls) and not (hasattr(cls, '__match_args__') and len(cls.__match_args__) >= n)
        isinstance_check = cst.Call(
            cst.Name("isinstance"),
            [cst.Arg(subject), cst.Arg(pattern.cls)],
        )

        hasattr_call = cst.Call(
            cst.Name("hasattr"),
            [cst.Arg(pattern.cls), cst.Arg(cst.SimpleString('"__match_args__"'))],
        )

        match_args_attr = cst.Attribute(pattern.cls, cst.Name("__match_args__"))
        len_check = cst.Comparison(
            left=cst.Call(cst.Name("len"), [cst.Arg(match_args_attr)]),
            comparisons=[
                cst.ComparisonTarget(
                    operator=cst.GreaterThanEqual(),
                    comparator=cst.Integer(str(num_positional)),
                ),
            ],
        )

        valid_match_args = cst.BooleanOperation(
            left=hasattr_call,
            operator=cst.And(),
            right=len_check,
        )

        invalid_match_args = cst.UnaryOperation(
            operator=cst.Not(),
            expression=valid_match_args.with_changes(
                lpar=[cst.LeftParen()],
                rpar=[cst.RightParen()],
            ),
        )

        error_condition = cst.BooleanOperation(
            left=isinstance_check,
            operator=cst.And(),
            right=invalid_match_args,
        )

        # Create body: raise TypeError("...")
        error_msg = (
            f"{cls_name}() accepts 0 positional sub-patterns ({num_positional} given)"
        )
        error_raise = cst.Raise(
            cst.Call(
                cst.Name("TypeError"),
                [cst.Arg(cst.SimpleString(f'"{error_msg}"'))],
            ),
        )

        error_body = cst.IndentedBlock([cst.SimpleStatementLine([error_raise])])

        return cst.If(test=error_condition, body=error_body)
