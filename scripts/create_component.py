import os
import argparse
from pathlib import Path

def create_component(templates_dir_path, output_path, placeholders):
    """
    Create files and directories based on a template, replacing placeholders.
    :param template_path: Path to the template structure directory.
    :param output_path: Directory where the new project will be created.
    :param placeholders: Dictionary of placeholders to replace in filenames and file content.
    """
    if placeholders['project_root'] == 'core':
        template_path = Path(templates_dir_path) / Path('core')
    if placeholders['project_root'] == 'base':
        template_path = Path(templates_dir_path) / Path('base')
    if placeholders['project_root'] == 'mixins':
        template_path = Path(templates_dir_path) / Path('mixins')
    if placeholders['project_root'] == 'swarmauri':
        template_path = Path(templates_dir_path) / Path('component')
    if placeholders['project_root'] == 'community':
        template_path = Path(templates_dir_path) / Path('component')
    if placeholders['project_root'] == 'experimental':
        template_path = Path(templates_dir_path) / Path('component')
    
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template path '{template_path}' does not exist.")
    
    # Ensure the output path exists
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Creating project at: {output_path}")
    print(f"Using template from: {template_path}")
    
    # Iterate over all files and directories in the template
    for root, dirs, files in os.walk(template_path):
        relative_root = Path(root).relative_to(template_path)
        target_root = output_path / relative_root

        # Replace placeholders in directory names
        target_root = Path(replace_placeholders(str(target_root), placeholders))
        target_root.mkdir(parents=True, exist_ok=True)

        for file in files:
            template_file = Path(root) / file
            target_file = target_root / replace_placeholders(file, placeholders)

            # Replace placeholders in file contents
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
                replaced_content = replace_placeholders(content, placeholders)
            
            # Write the replaced content to the new file
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(replaced_content)
            
            print(f"Created: {target_file}")

def replace_placeholders(text, placeholders):
    """
    Replace placeholders in a given text.
    :param text: The input text (filename or file content).
    :param placeholders: Dictionary of placeholders to replace.
    :return: Text with placeholders replaced.
    """
    for key, value in placeholders.items():
        text = text.replace("{{ "+key+" }}", value)
    return text

def main():
    parser = argparse.ArgumentParser(description="Custom Project Generator")
    parser.add_argument("--templates_dir", required=True, help="Path to the templates directory folder")
    parser.add_argument("--output", required=True, help="Base directory where the project will be created")
    parser.add_argument("--placeholders", nargs="+", help="Placeholder values in key=value format", required=True)
    args = parser.parse_args()

    # Parse placeholders into a dictionary
    placeholders = {}
    for placeholder in args.placeholders:
        key, value = placeholder.split("=", 1)
        placeholders[key] = value

    # Construct output path dynamically using placeholders
    if not all(key in placeholders for key in ["project_root", "package_name", "resource_kind", "component_name"]):
        raise ValueError("Missing required placeholders: project_root, package_name, resource_kind, component_name")

    if not placeholders["resource_kind"].endswith("s"):
        placeholders["resource_kind"] = placeholders["resource_kind"]+'s'
        
    placeholders["project_root"] = placeholders["project_root"].lower()
    placeholders["package_name"] = placeholders["package_name"].lower()
    placeholders["resource_kind"] = placeholders["resource_kind"].lower()
    dynamic_output_path = Path(args.output)
    # Generate the project
    create_component(args.templates_dir, dynamic_output_path, placeholders)

if __name__ == "__main__":
    main()
