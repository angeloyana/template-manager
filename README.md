# Template Manager

![GitHub Tag](https://img.shields.io/github/v/tag/angeloyana/template-manager)
![License](https://img.shields.io/github/license/angeloyana/template-manager)

**Tired of Repetitive Setup for New Projects?**

**Template Manager** is here to help! This command-line tool simplifies managing
templates for various programming stacks. With just a few commands, you can
quickly generate new projects, allowing you to focus on development and get
started as fast as possible.

## Installation

```
pip install git+https://github.com/angeloyana/template-manager.git
```

## Usage

Here's a quick demonstration on how to use **Template Manager**:

1. **Create Template Directory**:
    ```
    mkdir sample-template
    cd sample-template
    ```

2. **Initialize Template**:
    ```
    tpm init
    ```
    This generates `_template.json` inside `sample-template`.

3. **Modify the Placeholders**:  
    Inside `_template.json`:
    ```json
    {
      "placeholders": [
        {
          "name": "sampleName",
          "prompt": "Enter sample name:",
          "paths": ["README.md", "sample.json"]
        }
      ]
    }
    ```

4. **Create the Template Files**:  
    `sample-template/README.md`
    ```markdown
    # {{ sampleName }}
    
    This is a sample template.
    ```

    `sample-template/sample.json`
    ```json
    {
      "name": "{{ sampleName }}"
    }
    ```

5. **Save the Template**:
    ```
    tpm add --template-name sample
    ```

6. **Use the Template**:  
    To create a new project with that template, run:
    ```
    tpm generate --template-name sample --output new-project
    ```
    This will generate the template `sample` in the directory `new-project`.
    During the generation, it will prompt you for the placeholders specified
    inside the `_template.json`:
    ```
    ? Enter sample name: NewProject
    ```
    The tool will then replace the template files specified in the `paths`
    property using the templating engine [Jinja](https://jinja.palletsprojects.com/en/3.0.x/).

7. **Final Output**:  
    This generates a newly customized project and removes the `_template.json`
    inside `new-project`.

    `new-project/README.md`
    ```markdown
    # NewProject
    
    This is a sample template.
    ```

    `new-project/sample.json`
    ```json
    {
      "name": "NewProject"
    }
    ```

## License

This project is licensed under the [MIT License](./LICENSE)
