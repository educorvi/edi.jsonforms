# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_upload_field.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_upload_field.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a UploadField
  Given a logged-in site administrator
    and an add Form form
   When I type 'My UploadField' into the title field
    and I submit the form
   Then a UploadField with the title 'My UploadField' has been created

Scenario: As a site administrator I can view a UploadField
  Given a logged-in site administrator
    and a UploadField 'My UploadField'
   When I go to the UploadField view
   Then I can see the UploadField title 'My UploadField'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a UploadField 'My UploadField'
  Create content  type=Form  id=my-upload_field  title=My UploadField

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the UploadField view
  Go To  ${PLONE_URL}/my-upload_field
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a UploadField with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the UploadField title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
