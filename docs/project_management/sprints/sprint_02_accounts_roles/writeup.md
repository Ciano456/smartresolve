# Sprint 2 Write-Up

Sprint 2 focused on identity, access, and role awareness in the application. The main outcome of this sprint is that SmartResolve now has a working user authentication flow outside Django admin, along with a role structure based on Django groups that the application can use.

During this sprint, login and logout were implemented for the custom user model, with authentication based on email and password. A protected profile page was added and linked into the account flow, giving authenticated users a basic account area within the application. Logout was implemented as a `POST` action, which is the correct pattern for a state-changing action like ending a session.

Role and group support were also added. The core application groups, `Submitter`, `Support Staff`, and `Admin`, can be assigned to users through Django admin. The custom user model was extended with role-check properties so the application can check whether a user is an admin, submitter, or support staff member. A display-role property was also added so the assigned role can be shown clearly in the UI.

To support future permission control, a decorator layer was added in the accounts app. This gives the project a reusable pattern for role-based access checks in future views. The profile page was updated to display the real assigned role, and the account templates were improved visually to match the project branding.

Testing was introduced for this sprint. The accounts test suite covers the core authentication flow and user role properties, helping confirm that login, logout, access protection, and group-based role detection behave as expected.

## Completed Items

- login flow implemented
- logout flow implemented
- protected profile page added
- groups created for `Submitter`, `Support Staff`, and `Admin`
- users assignable to groups in admin
- role-check properties added to the custom user model
- display-role property added to the custom user model
- role shown on the profile page
- permission decorators/helpers added
- auth and role tests added
- account templates and layout refined

## Deliverable

By the end of Sprint 2, SmartResolve could authenticate users, recognise their assigned role, and expose that role both in code and in the UI.
