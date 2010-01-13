## Script (Python) "results_helper.cpy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=sorton='', view_mode='', b_size=''
##title=Turn the search POST into a GET
##

# Strip these fields out of the form and do not pass them on.  Pass all others back to the search form.
skip_fields = ['workspaceTop','workspaceBottom','form.button.Go']

request = context.REQUEST
form = request.form

for f in skip_fields:
    try:
        form.pop(f)
    except KeyError:
        pass

return state.set(context=context, **form)
