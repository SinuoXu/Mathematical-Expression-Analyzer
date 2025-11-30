"""
AST Visualization Module
Renders Abstract Syntax Trees as beautiful images using Graphviz.
"""

# Import from our local ast module (not Python's standard ast module)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ast_nodes import ASTNode, Number, Variable, BinOp, UnaryOp, FunctionCall
from typing import Optional


def ast_to_dot(node: ASTNode, node_id: int = 0, parent_id: Optional[int] = None) -> tuple:
    """
    Convert AST to DOT format for Graphviz.
    
    Args:
        node: AST node to convert
        node_id: Current node ID
        parent_id: Parent node ID (None for root)
    
    Returns:
        (dot_lines, next_node_id) where dot_lines is a list of DOT format lines
    """
    dot_lines = []
    current_id = node_id
    next_id = node_id + 1
    
    # Determine node label and style
    if isinstance(node, Number):
        label = str(node.value)
        shape = "circle"
        color = "#E8F5E9"  # Light green
        fontcolor = "#1B5E20"
    
    elif isinstance(node, Variable):
        label = node.name
        shape = "circle"
        color = "#E3F2FD"  # Light blue
        fontcolor = "#0D47A1"
    
    elif isinstance(node, BinOp):
        label = node.op
        shape = "diamond"
        color = "#FFF3E0"  # Light orange
        fontcolor = "#E65100"
    
    elif isinstance(node, UnaryOp):
        label = node.op
        shape = "diamond"
        color = "#FCE4EC"  # Light pink
        fontcolor = "#880E4F"
    
    elif isinstance(node, FunctionCall):
        label = node.func_name
        shape = "box"
        color = "#F3E5F5"  # Light purple
        fontcolor = "#4A148C"
    
    else:
        label = str(type(node).__name__)
        shape = "ellipse"
        color = "#EEEEEE"
        fontcolor = "#000000"
    
    # Add current node
    dot_lines.append(
        f'  node{current_id} [label="{label}", shape={shape}, '
        f'style=filled, fillcolor="{color}", fontcolor="{fontcolor}", '
        f'fontsize=14, fontname="Arial Bold"];'
    )
    
    # Add edge from parent if exists
    if parent_id is not None:
        dot_lines.append(f'  node{parent_id} -> node{current_id};')
    
    # Process children
    if isinstance(node, BinOp):
        # Left child
        left_lines, next_id = ast_to_dot(node.left, next_id, current_id)
        dot_lines.extend(left_lines)
        
        # Right child
        right_lines, next_id = ast_to_dot(node.right, next_id, current_id)
        dot_lines.extend(right_lines)
    
    elif isinstance(node, UnaryOp):
        # Operand
        operand_lines, next_id = ast_to_dot(node.operand, next_id, current_id)
        dot_lines.extend(operand_lines)
    
    elif isinstance(node, FunctionCall):
        # Argument
        arg_lines, next_id = ast_to_dot(node.arg, next_id, current_id)
        dot_lines.extend(arg_lines)
    
    return dot_lines, next_id


def render_ast(node: ASTNode, output_path: str = "ast_tree.png", format: str = "png", title: str = None) -> str:
    """
    Render AST as an image file.
    
    Args:
        node: AST node to render
        output_path: Output file path (default: ast_tree.png)
        format: Output format (png, pdf, svg, etc.)
        title: Optional title to display above the tree
    
    Returns:
        Path to the generated image file
    """
    try:
        import graphviz
    except ImportError:
        raise ImportError(
            "graphviz package is required for AST visualization.\n"
            "Install it with: pip install graphviz\n"
            "Also ensure Graphviz is installed on your system:\n"
            "  - macOS: brew install graphviz\n"
            "  - Ubuntu: sudo apt-get install graphviz\n"
            "  - Windows: Download from https://graphviz.org/download/"
        )
    
    # Generate DOT format
    dot_lines, _ = ast_to_dot(node)
    
    # Create DOT source
    dot_source = "digraph AST {\n"
    dot_source += "  rankdir=TB;\n"  # Top to bottom layout
    dot_source += "  node [fontname=\"Arial\"];\n"
    dot_source += "  edge [color=\"#666666\", penwidth=2];\n"
    dot_source += "  bgcolor=\"#FAFAFA\";\n"
    
    # Add title if provided
    if title:
        dot_source += f'  labelloc="t";\n'
        dot_source += f'  label="{title}";\n'
        dot_source += f'  fontsize=20;\n'
        dot_source += f'  fontname="Arial Bold";\n'
    
    dot_source += "\n".join(dot_lines)
    dot_source += "\n}"
    
    # Render using graphviz
    graph = graphviz.Source(dot_source)
    
    # Remove extension from output_path if present
    base_path = os.path.splitext(output_path)[0]
    
    # Render to file
    output_file = graph.render(base_path, format=format, cleanup=True)
    
    return output_file


def visualize_expression(expression: str, output_path: str = "ast_tree.png") -> str:
    """
    Parse and visualize an expression.
    
    Args:
        expression: Mathematical expression string
        output_path: Output file path (will be saved in images/ folder)
    
    Returns:
        Path to the generated image file
    """
    from parser import parse
    
    # Ensure images directory exists
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # Prepend images/ to output path if not already there
    if not output_path.startswith(images_dir + "/"):
        output_path = os.path.join(images_dir, output_path)
    
    ast = parse(expression)
    # Add expression as title
    return render_ast(ast, output_path, title=f"Expression: {expression}")


def create_comparison_visualization(expr1: str, expr2: str, output_path: str = "ast_comparison.png") -> str:
    """
    Create a side-by-side visualization of two expressions.
    
    Args:
        expr1: First expression string
        expr2: Second expression string
        output_path: Output file path (will be saved in images/ folder)
    
    Returns:
        Path to the generated image file
    """
    try:
        import graphviz
    except ImportError:
        raise ImportError("graphviz package is required for AST visualization.")
    
    from parser import parse
    
    # Ensure images directory exists
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # Prepend images/ to output path if not already there
    if not output_path.startswith(images_dir + "/"):
        output_path = os.path.join(images_dir, output_path)
    
    # Parse both expressions
    ast1 = parse(expr1)
    ast2 = parse(expr2)
    
    # Generate DOT for both trees
    dot_lines1, max_id1 = ast_to_dot(ast1, node_id=0)
    dot_lines2, _ = ast_to_dot(ast2, node_id=max_id1 + 1000)  # Offset IDs to avoid conflicts
    
    # Create DOT source with subgraphs
    dot_source = "digraph Comparison {\n"
    dot_source += "  rankdir=TB;\n"
    dot_source += "  node [fontname=\"Arial\"];\n"
    dot_source += "  edge [color=\"#666666\", penwidth=2];\n"
    dot_source += "  bgcolor=\"#FAFAFA\";\n"
    dot_source += "  \n"
    dot_source += "  subgraph cluster_0 {\n"
    dot_source += f'    label="{expr1}";\n'
    dot_source += "    fontsize=16;\n"
    dot_source += "    fontname=\"Arial Bold\";\n"
    dot_source += "    style=filled;\n"
    dot_source += "    color=\"#E3F2FD\";\n"
    dot_source += "    \n"
    dot_source += "\n".join("  " + line for line in dot_lines1)
    dot_source += "\n  }\n"
    dot_source += "  \n"
    dot_source += "  subgraph cluster_1 {\n"
    dot_source += f'    label="{expr2}";\n'
    dot_source += "    fontsize=16;\n"
    dot_source += "    fontname=\"Arial Bold\";\n"
    dot_source += "    style=filled;\n"
    dot_source += "    color=\"#FFF3E0\";\n"
    dot_source += "    \n"
    dot_source += "\n".join("  " + line for line in dot_lines2)
    dot_source += "\n  }\n"
    dot_source += "}"
    
    # Render using graphviz
    graph = graphviz.Source(dot_source)
    
    # Remove extension from output_path if present
    base_path = os.path.splitext(output_path)[0]
    
    # Render to file
    output_file = graph.render(base_path, format="png", cleanup=True)
    
    return output_file


if __name__ == "__main__":
    # Example usage
    print("AST Visualization Examples")
    print("=" * 70)
    
    examples = [
        ("x+1", "simple_addition.png"),
        ("(x+1)^2", "polynomial_square.png"),
        ("sin(x+y)", "function_call.png"),
        ("x^2+2*x+1", "quadratic.png"),
        ("-x^2", "unary_minus.png"),
    ]
    
    for expr, filename in examples:
        try:
            output = visualize_expression(expr, filename)
            print(f"✓ Generated: {output} for expression: {expr}")
        except Exception as e:
            print(f"✗ Error for {expr}: {e}")
    
    # Comparison example
    try:
        output = create_comparison_visualization("x+1", "1+x", "comparison.png")
        print(f"\n✓ Generated comparison: {output}")
    except Exception as e:
        print(f"\n✗ Error creating comparison: {e}")
