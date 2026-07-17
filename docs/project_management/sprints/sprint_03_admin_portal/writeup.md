# Sprint 3 Write-Up

Sprint 3 focused on building a dedicated admin-facing user management area inside SmartResolve so that administrators can manage users directly through the application UI rather than relying only on Django admin. This sprint introduced the `admin_portal` app as a separate area of the system and extended the existing role-based access model established in Sprint 2.

The first part of the sprint was setting up the admin portal structure. A dedicated `admin_portal` app was created and wired into the main project. Admin-only access was enforced using the existing `admin_required` decorator from the `accounts` app, ensuring that only users assigned to the `Admin` group can access portal routes. A branded admin portal landing page was then built to act as the entry point for Sprint 3 functionality.

After the portal entry page was established, a full user management flow was developed. This included a user list page that displays all users in the system along with their email address, current role, and account status. A user detail page was also added to give administrators a focused view of an individual account.

Administrator-led user creation was implemented using a custom `AdminPortalUserCreateForm` based on Django's `UserCreationForm`, allowing secure password handling to be reused while supporting the custom user model. The form allows administrators to create new users, assign one application role from the UI, and set initial account status.

User editing was added through a dedicated edit form and view. The edit form allows administrators to update user information, change the assigned role, and activate or deactivate the account. Since role is not a direct model field, custom form logic initialises the current role correctly when editing an existing user.

Activate and deactivate actions were implemented as explicit POST-only admin actions. This avoids unsafe state changes through GET requests and keeps behaviour aligned with Django security best practices.

The sprint also included UI consistency work. Admin portal pages were styled to match the existing visual direction. Shared navigation patterns were refined so navigation can respond to the logged-in user's role.

Tailwind was moved away from CDN usage to a proper build setup through npm, with a project-level configuration, source stylesheet, compiled output file, and Django static integration.

Testing was added for the admin portal. View tests confirm that admin pages are accessible only to admin users, non-admin users are redirected, and activate/deactivate actions behave correctly. Form tests cover creation, duplicate email rejection, password mismatch handling, role assignment, edit form role initialisation, and active status updates.

Later review cleanup also strengthened the admin portal configuration area. Lookup `code` fields are now locked after a lookup value has been created, because ticket workflow logic depends on stable codes such as `OPEN`, `IN_PROGRESS`, and `CLOSED`. The admin all-ticket list is also paginated to avoid rendering every ticket in a larger dataset. Regression tests were added for both behaviours.

## Deliverable

Sprint 3 delivered a working admin portal for user management. Administrators can access a dedicated admin area, create users, edit users, assign roles from the UI, and manage account activation status.
