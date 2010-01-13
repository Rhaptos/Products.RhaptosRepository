from ZTUtils import make_query

request = container.REQUEST
portal = context.portal_url.getPortalObject()

wgprefix = 'GroupWorkspaces/'
lensprefix = 'lenses/'

if context.portal_membership.isAnonymousUser():
  return

objects = request.get('ids',[])
psm = ''

if objects:
  workspace = request.get('workspace', None)
  if workspace is None:
      button = request.get('form.button.WorkspaceAdd', None)
      if button == "AddBottom":
        workspace = request.get('workspaceBottom','__home__')
      else:
        workspace = request.get('workspaceTop','__home__')
  
  isWorkspace = True
  action = 'view'
  if workspace == '__home__':
    target = context.portal_membership.getHomeFolder()
    home = context.portal_membership.getHomeUrl()
  elif workspace.startswith(wgprefix):
    workspace = workspace[len(wgprefix):]
    target = context.portal_groups.getGroupareaFolder(workspace)
    home = context.portal_groups.getGroupareaURL(workspace)
  elif workspace.startswith(lensprefix):
    isWorkspace = False
    workspace = workspace[len(lensprefix):]
    target = getattr(context.lens_tool.getIndividualFolder(), workspace)
    home = target.absolute_url()
    action = "lens_content_view"

  for objectId in objects:
    content = portal.content.getRhaptosObject(objectId, 'latest')
    exists = getattr(target, objectId, None)
    if exists is None:
        if isWorkspace:
            target.invokeFactory(id=objectId, type_name=content.portal_type)
            object = target[objectId]
            object.setState('published')
            object.checkout(objectId)
        else:   # lens
            version = content.version
            target.lensAdd(target.absolute_url(1), objectId, version, batched=True)
    else:
        if isWorkspace:
            import transaction
            transaction.abort()
            psm = "At least one selected item already present: %s" % objectId
            request.response.redirect("/content/search?%s" % make_query({'portal_status_message':psm})) #request.form, 
            return

  if not isWorkspace:
      target.reindexObject(idxs=['count'])
      time = context.lens_tool.catalogQueueInfo()
      time = time and time[1] or 0
      if time > 0.1:
          psm = "The system is processing lens changes. These additions should be viewable on content in %0.1f minutes." % time

  if psm:
    request.response.redirect("%s/%s?portal_status_message=%s" % (home, action, psm))
  else:
    request.response.redirect("%s/%s" % (home, action))

else:
  psm=context.translate("message_nothing_selected", domain="rhaptos", default="Nothing selected.")
  request.response.redirect(request.HTTP_REFERER+'&portal_status_message='+psm)

return "You should not be seeing this message."
# we have to return something or else the redirect doesn't take, for some reason. dunno why.
# FIXME: the whole search form handling is pretty idiosyncratic; probably this wouldn't matter
# if it properly used FormController, etc.
