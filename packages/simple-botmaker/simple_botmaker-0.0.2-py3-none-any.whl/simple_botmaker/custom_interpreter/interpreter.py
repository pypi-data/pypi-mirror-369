import sys
import ast
import importlib.util
import builtins

allowed_files = ["simple_botmaker/high_level_functions.py", "simple_botmaker/low_level_functions.py", "simple_botmaker/globals.py"]
script_path = sys.argv[-1]
allowed_env = {}

def load_module(filepath):
    spec = importlib.util.spec_from_file_location("mod_" + filepath.replace("/", "_").replace(".", "_"), filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

for filepath in allowed_files:
    mod = load_module(filepath)
    for name in dir(mod):
        if not name.startswith("__"):
            allowed_env[name] = getattr(mod, name)

with open(script_path, "r") as f:
    script_source = f.read()

class DefinitionRemover(ast.NodeTransformer):
    def visit_Import(self, node):
        new_names = [alias for alias in node.names if alias.name != "Definitions"]
        if new_names:
            node.names = new_names
            return node
        return None
    def visit_ImportFrom(self, node):
        if node.module == "Definitions":
            return None
        return node
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "Definitions":
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return node

class NameChecker(ast.NodeVisitor):
    def __init__(self, allowed):
        self.allowed = set(allowed)
        self.scopes = [set()]
    def push_scope(self):
        self.scopes.append(set())
    def pop_scope(self):
        self.scopes.pop()
    def add_name(self, name):
        self.scopes[-1].add(name)
    def is_defined(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False
    def visit_FunctionDef(self, node):
        self.add_name(node.name)
        self.push_scope()
        for arg in node.args.args:
            self.add_name(arg.arg)
        if node.args.vararg:
            self.add_name(node.args.vararg.arg)
        for arg in node.args.kwonlyargs:
            self.add_name(arg.arg)
        if node.args.kwarg:
            self.add_name(node.args.kwarg.arg)
        self.generic_visit(node)
        self.pop_scope()
    def visit_ClassDef(self, node):
        self.add_name(node.name)
        self.push_scope()
        self.generic_visit(node)
        self.pop_scope()
    def visit_Assign(self, node):
        for target in node.targets:
            self.handle_target(target)
        self.generic_visit(node)
    def visit_AnnAssign(self, node):
        self.handle_target(node.target)
        self.generic_visit(node)
    def visit_AugAssign(self, node):
        self.handle_target(node.target)
        self.generic_visit(node)
    def handle_target(self, node):
        if isinstance(node, ast.Name):
            self.add_name(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                self.handle_target(elt)
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name != "Definitions":
                raise Exception("Imports not allowed")
        self.generic_visit(node)
    def visit_ImportFrom(self, node):
        if node.module != "Definitions":
            raise Exception("Imports not allowed")
        self.generic_visit(node)
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not self.is_defined(node.id) and node.id not in self.allowed and not hasattr(builtins, node.id):
                raise Exception(f"Usage of '{node.id}' is not allowed")
        self.generic_visit(node)

class StaticChecker(NameChecker):
    def __init__(self, allowed):
        super().__init__(allowed)
        self.errors = []
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name != "Definitions":
                self.errors.append(f"Line {node.lineno}: Imports not allowed")
        self.generic_visit(node)
    def visit_ImportFrom(self, node):
        if node.module != "Definitions":
            self.errors.append(f"Line {node.lineno}: Imports not allowed")
        self.generic_visit(node)
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if not self.is_defined(node.id) and node.id not in self.allowed and not hasattr(builtins, node.id):
                self.errors.append(f"Line {node.lineno}: Usage of '{node.id}' is not allowed")
        self.generic_visit(node)

def static_check(script_path, allowed_env):
    with open(script_path, "r") as f:
        source = f.read()
    tree = ast.parse(source, mode="exec")
    checker = StaticChecker(allowed_env.keys())
    checker.visit(tree)
    for error in checker.errors:
        print(error)
    if not checker.errors:
        print("No issues found")

def main():
    """Main entry point for the console script."""
    if len(sys.argv) < 2:
        print("Usage: simple-botmaker-interpreter [--check] <script.py>")
        sys.exit(1)
    
    script_path = sys.argv[-1]
    
    if not os.path.exists(script_path):
        print(f"Error: Script file '{script_path}' not found.")
        sys.exit(1)
    
    # Load allowed environment
    allowed_env = {}
    for filepath in allowed_files:
        if os.path.exists(filepath):
            mod = load_module(filepath)
            for name in dir(mod):
                if not name.startswith("__"):
                    allowed_env[name] = getattr(mod, name)
    
    with open(script_path, "r") as f:
        script_source = f.read()
    
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        static_check(script_path, allowed_env)
    else:
        tree = ast.parse(script_source, mode="exec")
        tree = DefinitionRemover().visit(tree)
        ast.fix_missing_locations(tree)
        checker = NameChecker(allowed_env.keys())
        checker.visit(tree)
        env = allowed_env.copy()
        exec(compile(tree, script_path, "exec"), env)

if __name__ == "__main__":
    main()