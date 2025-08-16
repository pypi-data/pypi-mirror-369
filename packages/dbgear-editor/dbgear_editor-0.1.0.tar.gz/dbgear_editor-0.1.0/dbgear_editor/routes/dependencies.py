"""
Dependency visualization routes.
Handles ER diagram and dependency analysis endpoints.
"""

from fasthtml.common import *
from starlette.requests import Request
from dbgear.misc.dependencies import TableDependencyAnalyzer
from dbgear.models.exceptions import DBGearError

from ..layout import layout
from ..project import get_current_project
from ..ui.dependencies import (
    render_schema_er_diagram,
    render_table_dependency_view
)


def register_dependency_routes(rt):
    """Register dependency visualization routes."""
    
    @rt('/schemas/{schema_name}/dependencies')
    def schema_dependencies(schema_name: str, request: Request):
        """Display ER diagram for entire schema."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return RedirectResponse(url="/")
            
            # Validate schema exists
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return layout(
                    title="Schema Not Found",
                    content=Div(
                        H1("Schema Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Schema '{schema_name}' does not exist in this project.", cls="text-gray-700 mb-4"),
                        A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    )
                )
            
            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )
            
            # Get schema object
            schema = project.schema_manager.schemas[schema_name]
            
            # Build graph data structure
            nodes = []
            edges = []
            
            # Add all tables as nodes
            for table_name, table_obj in schema.tables.tables.items():
                nodes.append({
                    "id": f"{schema_name}.{table_name}",
                    "type": "table",
                    "schema_name": schema_name,
                    "table_name": table_name,
                    "label": table_name
                })
            
            # Add all views as nodes
            for view_name, view_obj in schema.views.views.items():
                nodes.append({
                    "id": f"{schema_name}.{view_name}",
                    "type": "view",
                    "schema_name": schema_name,
                    "view_name": view_name,
                    "label": view_name
                })
            
            # Analyze dependencies for each table to create edges
            for table_name in schema.tables.tables.keys():
                try:
                    deps = analyzer.analyze(
                        schema_name=schema_name,
                        table_name=table_name,
                        left_level=0,  # We only need right side for schema graph
                        right_level=2
                    )
                    
                    # Create edges from dependencies
                    for level_key, level_deps in deps["right"].items():
                        for dep in level_deps:
                            if dep["type"] == "relation" and dep["table_name"]:
                                # Foreign key relationship
                                edges.append({
                                    "source": f"{schema_name}.{table_name}",
                                    "target": f"{dep['schema_name']}.{dep['table_name']}",
                                    "type": "relation",
                                    "label": dep["object_name"],
                                    "details": dep["details"]
                                })
                
                except Exception as e:
                    # Skip tables that can't be analyzed
                    print(f"Warning: Could not analyze dependencies for {table_name}: {e}")
                    continue
            
            graph_data = {
                "nodes": nodes,
                "edges": edges,
                "schema_name": schema_name,
                "max_level": 2
            }
            
            # Render ER diagram page
            content = render_schema_er_diagram(schema_name, graph_data)
            
            return layout(
                content,
                f"ER Diagram - {schema_name} - DBGear Editor",
                str(request.url.path)
            )
            
        except DBGearError as e:
            return layout(
                Div(
                    H1("Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Error - DBGear Editor",
                str(request.url.path)
            )
        except Exception as e:
            return layout(
                Div(
                    H1("Internal Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An unexpected error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Internal Error - DBGear Editor",
                str(request.url.path)
            )
    
    @rt('/schemas/{schema_name}/tables/{table_name}/dependencies')
    def table_dependencies(schema_name: str, table_name: str, request: Request):
        """Display dependency analysis for specific table."""
        try:
            # Get current project
            project = get_current_project()
            if not project or not project.is_loaded():
                return RedirectResponse(url="/")
            
            # Validate schema and table exist
            schemas = project.get_schemas()
            if schema_name not in schemas:
                return layout(
                    Div(
                        H1("Schema Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Schema '{schema_name}' does not exist in this project.", cls="text-gray-700 mb-4"),
                        A("← Back to Dashboard", href="/", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    ),
                    "Schema Not Found - DBGear Editor",
                    str(request.url.path)
                )
            
            schema = project.schema_manager.schemas[schema_name]
            if table_name not in schema.tables.tables:
                return layout(
                    Div(
                        H1("Table Not Found", cls="text-2xl font-bold text-red-600 mb-4"),
                        P(f"Table '{table_name}' does not exist in schema '{schema_name}'.", cls="text-gray-700 mb-4"),
                        A(f"← Back to Schema", href=f"/schemas/{schema_name}", cls="text-blue-600 hover:text-blue-800"),
                        cls="container mx-auto px-4 py-8"
                    ),
                    "Table Not Found - DBGear Editor",
                    str(request.url.path)
                )
            
            # Initialize dependency analyzer
            analyzer = TableDependencyAnalyzer(
                schema_manager=project.schema_manager,
                project_folder=project.project_path
            )
            
            # Analyze table dependencies
            dependencies = analyzer.analyze(
                schema_name=schema_name,
                table_name=table_name,
                left_level=3,
                right_level=3
            )
            
            # Render dependency view
            content = render_table_dependency_view(schema_name, table_name, dependencies)
            
            return layout(
                content,
                f"Dependencies - {table_name} - DBGear Editor",
                str(request.url.path)
            )
            
        except DBGearError as e:
            return layout(
                Div(
                    H1("Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A(f"← Back to Table", href=f"/schemas/{schema_name}/tables/{table_name}", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Error - DBGear Editor",
                str(request.url.path)
            )
        except Exception as e:
            return layout(
                Div(
                    H1("Internal Error", cls="text-2xl font-bold text-red-600 mb-4"),
                    P(f"An unexpected error occurred: {str(e)}", cls="text-gray-700 mb-4"),
                    A(f"← Back to Table", href=f"/schemas/{schema_name}/tables/{table_name}", cls="text-blue-600 hover:text-blue-800"),
                    cls="container mx-auto px-4 py-8"
                ),
                "Internal Error - DBGear Editor",
                str(request.url.path)
            )