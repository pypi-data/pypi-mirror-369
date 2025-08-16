"""
ER diagram component for rendering Mermaid diagrams.
Converts dependency analysis data to Mermaid ER diagram syntax.
"""

from typing import Dict, List, Any, Optional


def generate_mermaid_er_diagram(graph_data: Dict[str, Any], focus_table: Optional[str] = None) -> str:
    """
    Generate Mermaid ER diagram syntax from dependency graph data.
    
    Args:
        graph_data: Graph data from TableDependencyAnalyzer
        focus_table: Optional table name to highlight as center of diagram
        
    Returns:
        Mermaid ER diagram syntax string
    """
    mermaid_code = "erDiagram\n"
    
    # Track processed entities and relationships
    entities = set()
    relationships = []
    
    # Process nodes (tables and views)
    for node in graph_data.get('nodes', []):
        if node['type'] == 'table':
            table_name = _clean_identifier(node['table_name'])
            entities.add(table_name)
            
            # Add table definition
            if focus_table and node['table_name'] == focus_table:
                mermaid_code += f"    {table_name} {{\n"
                mermaid_code += f"        string id PK \"Primary Key\"\n"
                mermaid_code += f"        string name \"Table Name\"\n"
                mermaid_code += "    }\n"
            else:
                mermaid_code += f"    {table_name}\n"
    
    # Process edges (relationships)
    for edge in graph_data.get('edges', []):
        if edge['type'] == 'relation':
            source_table = _extract_table_name(edge['source'])
            target_table = _extract_table_name(edge['target'])
            
            if source_table and target_table:
                source_clean = _clean_identifier(source_table)
                target_clean = _clean_identifier(target_table)
                
                # Ensure both entities exist
                entities.add(source_clean)
                entities.add(target_clean)
                
                # Determine relationship cardinality
                cardinality = _determine_cardinality(edge.get('details', {}))
                
                # Add relationship
                relationship = f"    {source_clean} {cardinality} {target_clean} : \"{edge.get('label', 'references')}\""
                if relationship not in relationships:
                    relationships.append(relationship)
    
    # Add all relationships
    for relationship in relationships:
        mermaid_code += relationship + "\n"
    
    return mermaid_code


def generate_table_dependency_diagram(dependencies: Dict[str, Any]) -> str:
    """
    Generate Mermaid diagram for individual table dependencies.
    
    Args:
        dependencies: Output from TableDependencyAnalyzer.analyze()
        
    Returns:
        Mermaid ER diagram syntax string
    """
    mermaid_code = "erDiagram\n"
    
    # Central table
    target_table = dependencies.get('target_table', {})
    center_table = _clean_identifier(target_table.get('table_name', 'Unknown'))
    
    mermaid_code += f"    {center_table} {{\n"
    mermaid_code += f"        string id PK \"Primary Key\"\n"
    mermaid_code += "    }\n"
    
    entities = {center_table}
    relationships = []
    
    # Process left dependencies (tables referencing this one)
    for level_key, deps in dependencies.get('left', {}).items():
        for dep in deps:
            if dep['type'] == 'relation' and dep.get('table_name'):
                ref_table = _clean_identifier(dep['table_name'])
                entities.add(ref_table)
                
                # Foreign key relationship
                cardinality = "||--o{"
                relationship = f"    {center_table} {cardinality} {ref_table} : \"referenced by\""
                if relationship not in relationships:
                    relationships.append(relationship)
    
    # Process right dependencies (tables this one references)
    for level_key, deps in dependencies.get('right', {}).items():
        for dep in deps:
            if dep['type'] == 'relation' and dep.get('table_name'):
                target_table_name = _clean_identifier(dep['table_name'])
                entities.add(target_table_name)
                
                # Foreign key relationship
                cardinality = "}o--||"
                relationship = f"    {center_table} {cardinality} {target_table_name} : \"references\""
                if relationship not in relationships:
                    relationships.append(relationship)
    
    # Add relationships
    for relationship in relationships:
        mermaid_code += relationship + "\n"
    
    return mermaid_code


def _clean_identifier(identifier: str) -> str:
    """Clean identifier for Mermaid syntax compatibility."""
    if not identifier:
        return "Unknown"
    
    # Replace special characters with underscores
    cleaned = identifier.replace('-', '_').replace(' ', '_').replace('.', '_')
    
    # Ensure it starts with a letter or underscore
    if cleaned and not (cleaned[0].isalpha() or cleaned[0] == '_'):
        cleaned = f"T_{cleaned}"
    
    return cleaned or "Unknown"


def _extract_table_name(node_id: str) -> Optional[str]:
    """Extract table name from node ID (format: schema.table)."""
    if '.' in node_id:
        return node_id.split('.', 1)[1]
    return node_id


def _determine_cardinality(details: Dict[str, Any]) -> str:
    """
    Determine Mermaid cardinality notation from relationship details.
    
    Returns:
        Mermaid cardinality string (e.g., "||--o{", "}o--||")
    """
    # Default to many-to-one relationship (typical for FK)
    cardinality_source = details.get('cardinarity_source', 'many')
    cardinality_target = details.get('cardinarity_target', 'one')
    
    # Map DBGear cardinality to Mermaid notation
    source_notation = "o{" if cardinality_source == 'many' else "||"
    target_notation = "}o" if cardinality_target == 'many' else "||"
    
    return f"{source_notation}--{target_notation}"


def create_dependency_summary_text(dependencies: Dict[str, Any]) -> List[str]:
    """
    Create a text summary of dependencies for display.
    
    Args:
        dependencies: Output from TableDependencyAnalyzer.analyze()
        
    Returns:
        List of summary strings
    """
    summary = []
    target_table = dependencies.get('target_table', {})
    table_name = target_table.get('table_name', 'Unknown')
    
    # Count dependencies
    left_count = sum(len(deps) for deps in dependencies.get('left', {}).values())
    right_count = sum(len(deps) for deps in dependencies.get('right', {}).values())
    
    summary.append(f"Table: {table_name}")
    summary.append(f"Referenced by: {left_count} objects")
    summary.append(f"References: {right_count} objects")
    
    # Detail breakdown
    for side, label in [('left', 'Referenced by'), ('right', 'References')]:
        deps_by_type = {}
        for level_deps in dependencies.get(side, {}).values():
            for dep in level_deps:
                dep_type = dep['type']
                if dep_type not in deps_by_type:
                    deps_by_type[dep_type] = 0
                deps_by_type[dep_type] += 1
        
        if deps_by_type:
            type_summary = ", ".join([f"{count} {dep_type}(s)" for dep_type, count in deps_by_type.items()])
            summary.append(f"  {label}: {type_summary}")
    
    return summary