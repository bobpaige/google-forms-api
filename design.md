# Google Forms API

This project creates Google forms form a configuration file so users can review resources and provide feedback.
Once they provide feedback in one form, they are prompted to continue to the next in the chain, which will include
a link to the resource to be reviewed.

## Requirements

The purpose of this API is to make it easier to define forms with the following properties:

1. Questions

- The purpose of the forms is to provide feedback on another resource (video, audio, or document)
- The forms will have similar questions, so duplicating them across forms is easier from a configuration file.

2. Descriptions

- The header of each form will contain a block of text describing the purpose of the form, along with links to resources to be reviewed 

3. Follow Up

- The message displayed after the form is submitted will include a link to the next form.

4. Idempotent

- Small changes to the input configuration file should update existing forms, not replace them (so the API for each form is stable)
- Running the program with _no_ changes to the inputs should produce no changes to existing forms.

In this way, the program functions similarly to tools such as Terraform or CloudFormation, but for Google Forms.


## Inputs

The inputs for the entire project (which is a collection of forms) is a single YAML file. 

The file defines multiple forms. Each form includes the requirements listed above, such as:
- description with link to resources to be reviewed
- response message that includes a link to the next form