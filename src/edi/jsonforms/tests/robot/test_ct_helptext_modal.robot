# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.jsonforms -t test_helptext_modal.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.jsonforms.testing.EDI_JSONFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/jsonforms/tests/robot/test_helptext_modal.robot
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

Scenario: As a site administrator I can add a Helptext Modal
  Given a logged-in site administrator
    and an add Form form
   When I type 'My Helptext Modal' into the title field
    and I submit the form
   Then a Helptext Modal with the title 'My Helptext Modal' has been created

Scenario: As a site administrator I can view a Helptext Modal
  Given a logged-in site administrator
    and a Helptext Modal 'My Helptext Modal'
   When I go to the Helptext Modal view
   Then I can see the Helptext Modal title 'My Helptext Modal'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Form form
  Go To  ${PLONE_URL}/++add++Form

a Helptext Modal 'My Helptext Modal'
  Create content  type=Form  id=my-helptext_modal  title=My Helptext Modal

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Helptext Modal view
  Go To  ${PLONE_URL}/my-helptext_modal
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Helptext Modal with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Helptext Modal title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
