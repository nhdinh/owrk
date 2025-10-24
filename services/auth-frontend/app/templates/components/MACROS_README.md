# Template Macros Documentation

This document describes the reusable Jinja2 macros available in `components/macros.html`.

## How to Use Macros

Import the macros at the top of your template:

```jinja2
{% from 'components/macros.html' import avatar_circle, status_badge, alert, pagination %}
```

Then use them anywhere in your template.

---

## Available Macros

### 1. `avatar_circle(name, size, font_size, bg_color)`

Creates a circular avatar with the first letter of a name.

**Parameters:**
- `name` (str, required): The name to display (first letter will be shown)
- `size` (str, optional): CSS width/height (default: '40px')
- `font_size` (str, optional): CSS font size (default: '16px')
- `bg_color` (str, optional): Bootstrap color (default: 'primary')

**Example:**
```jinja2
{{ avatar_circle(user.full_name) }}
{{ avatar_circle(user.full_name, '60px', '24px', 'success') }}
```

**Output:**
- A rounded circle with background color and initial letter

---

### 2. `status_badge(is_active, active_text, inactive_text)`

Displays a status badge (active/inactive).

**Parameters:**
- `is_active` (bool, required): Whether the status is active
- `active_text` (str, optional): Text for active state (default: 'Hoạt động')
- `inactive_text` (str, optional): Text for inactive state (default: 'Ngừng hoạt động')

**Example:**
```jinja2
{{ status_badge(user.is_active) }}
{{ status_badge(role.is_active, 'Enabled', 'Disabled') }}
```

---

### 3. `mfa_badge(mfa_enabled)`

Shows MFA status with shield icon.

**Parameters:**
- `mfa_enabled` (bool, required): Whether MFA is enabled

**Example:**
```jinja2
{{ mfa_badge(user.mfa_enabled) }}
```

---

### 4. `alert(message, type, dismissible, icon)`

Bootstrap alert with optional icon and dismiss button.

**Parameters:**
- `message` (str, required): Alert message content
- `type` (str, optional): Bootstrap alert type (default: 'info')
  - Options: 'info', 'success', 'warning', 'danger'
- `dismissible` (bool, optional): Show close button (default: true)
- `icon` (str, optional): Bootstrap icon name (auto-selects based on type if not provided)

**Example:**
```jinja2
{{ alert('User created successfully!', 'success') }}
{{ alert('Invalid input', 'danger', false, 'exclamation-triangle') }}
```

---

### 5. `action_buttons(view_url, edit_url, delete_url, custom_buttons)`

Creates a button group with common actions (view, edit, delete).

**Parameters:**
- `view_url` (str, optional): URL for view action
- `edit_url` (str, optional): URL for edit action
- `delete_url` (str, optional): URL for delete action (includes confirmation)
- `custom_buttons` (list, optional): List of custom button dicts

**Custom Button Dict:**
```python
{
    'icon': 'lock',           # Bootstrap icon name
    'color': 'warning',       # Bootstrap color
    'title': 'Lock user',     # Tooltip text
    'onclick': 'lockUser()',  # JS function
    'data_attrs': {           # Optional data attributes
        'user-id': '123'
    }
}
```

**Example:**
```jinja2
{{ action_buttons(
    view_url=url_for('users.detail', user_id=user.id),
    edit_url=url_for('users.edit', user_id=user.id),
    delete_url=url_for('users.delete', user_id=user.id)
) }}

{{ action_buttons(
    custom_buttons=[
        {'icon': 'lock', 'color': 'warning', 'title': 'Lock', 'onclick': 'lockUser()'}
    ]
) }}
```

---

### 6. `pagination(current_page, total_pages, base_url, query_params)`

Creates a pagination component.

**Parameters:**
- `current_page` (int, optional): Current page number (default: 1)
- `total_pages` (int, optional): Total number of pages (default: 1)
- `base_url` (str, optional): Base URL for page links (default: '#')
- `query_params` (dict, optional): Additional query parameters (default: {})

**Example:**
```jinja2
{{ pagination(
    current_page=2,
    total_pages=10,
    base_url='/users',
    query_params={'search': 'john', 'role': 'admin'}
) }}
```

**Output:**
- Previous/Next buttons
- Page numbers (with ellipsis for large page counts)
- Preserves query parameters across pages

---

### 7. `empty_state(icon, title, message, action_text, action_url)`

Displays an empty state placeholder.

**Parameters:**
- `icon` (str, optional): Bootstrap icon name (default: 'inbox')
- `title` (str, optional): Heading text (default: 'Không có dữ liệu')
- `message` (str, optional): Description text
- `action_text` (str, optional): Button text
- `action_url` (str, optional): Button URL

**Example:**
```jinja2
{{ empty_state(
    icon='person-plus',
    title='No users found',
    message='Get started by adding your first user',
    action_text='Add User',
    action_url='/users/create'
) }}
```

---

### 8. `card_header(title, icon, badge_text, badge_color, action_button)`

Creates a card header with optional badge and action button.

**Parameters:**
- `title` (str, required): Header title
- `icon` (str, optional): Bootstrap icon name
- `badge_text` (str, optional): Badge content
- `badge_color` (str, optional): Bootstrap badge color (default: 'info')
- `action_button` (dict, optional): Action button configuration

**Action Button Dict:**
```python
{
    'text': 'Add User',        # Button text
    'icon': 'plus-circle',     # Bootstrap icon
    'color': 'primary',        # Bootstrap color
    'modal': 'createModal',    # Modal ID (optional)
    'onclick': 'doAction()'    # JS function (optional)
}
```

**Example:**
```jinja2
{{ card_header(
    'User List',
    icon='people',
    badge_text='25',
    badge_color='primary',
    action_button={
        'text': 'Add User',
        'icon': 'plus-circle',
        'modal': 'createUserModal'
    }
) }}
```

---

### 9. `loading_spinner(text, size)`

Shows a loading spinner with text.

**Parameters:**
- `text` (str, optional): Loading message (default: 'Đang tải...')
- `size` (str, optional): Spinner size ('sm' or leave empty for default)

**Example:**
```jinja2
{{ loading_spinner() }}
{{ loading_spinner('Loading users...', 'sm') }}
```

---

### 10. `form_field(type, name, label, value, required, placeholder, help_text, options)`

Creates a form field with label and validation.

**Parameters:**
- `type` (str, optional): Input type (default: 'text')
  - Options: 'text', 'email', 'password', 'number', 'tel', 'select', 'textarea'
- `name` (str, required): Field name
- `label` (str, required): Field label
- `value` (str, optional): Default value
- `required` (bool, optional): Whether field is required (default: false)
- `placeholder` (str, optional): Placeholder text
- `help_text` (str, optional): Help text below field
- `options` (list, optional): Options for select fields

**Select Options Format:**
```python
[
    {'value': '1', 'label': 'Option 1'},
    {'value': '2', 'label': 'Option 2'}
]
```

**Example:**
```jinja2
{{ form_field(
    type='email',
    name='user_email',
    label='Email Address',
    required=true,
    placeholder='user@example.com',
    help_text='We will never share your email'
) }}

{{ form_field(
    type='select',
    name='role_id',
    label='Role',
    required=true,
    placeholder='Select a role',
    options=[
        {'value': '1', 'label': 'Admin'},
        {'value': '2', 'label': 'User'}
    ]
) }}
```

---

### 11. `timestamp(datetime, icon, show_time)`

Formats and displays a timestamp.

**Parameters:**
- `datetime` (datetime, required): DateTime object or formatted string
- `icon` (str, optional): Bootstrap icon name (default: 'calendar')
- `show_time` (bool, optional): Show time portion (default: true)

**Example:**
```jinja2
{{ timestamp(user.created_at) }}
{{ timestamp(user.last_login_at, 'clock', true) }}
{{ timestamp(user.birth_date, 'calendar', false) }}
```

---

### 12. `user_info(user, show_role, show_email, avatar_size)`

Displays user information with avatar (for lists/tables).

**Parameters:**
- `user` (object, required): User object with full_name, email, role
- `show_role` (bool, optional): Display user's role (default: true)
- `show_email` (bool, optional): Display user's email (default: true)
- `avatar_size` (str, optional): Avatar size (default: '40px')

**Example:**
```jinja2
{{ user_info(user) }}
{{ user_info(user, show_role=false, avatar_size='50px') }}
```

---

### 13. `confirm_modal(id, title, message, confirm_text, cancel_text, confirm_color)`

Creates a confirmation modal dialog.

**Parameters:**
- `id` (str, required): Modal ID
- `title` (str, required): Modal title
- `message` (str, required): Confirmation message
- `confirm_text` (str, optional): Confirm button text (default: 'Xác nhận')
- `cancel_text` (str, optional): Cancel button text (default: 'Hủy')
- `confirm_color` (str, optional): Confirm button color (default: 'primary')

**Example:**
```jinja2
{{ confirm_modal(
    'deleteUserModal',
    'Delete User',
    'Are you sure you want to delete this user? This action cannot be undone.',
    'Delete',
    'Cancel',
    'danger'
) }}

{# Trigger the modal with a button #}
<button data-bs-toggle="modal" data-bs-target="#deleteUserModal">
    Delete
</button>

{# Handle confirmation with JavaScript #}
<script>
document.getElementById('deleteUserModal_confirm').addEventListener('click', function() {
    // Perform delete action
});
</script>
```

---

## Complete Example

Here's a complete example of using multiple macros in a template:

```jinja2
{% extends 'layouts/dashboard.html' %}
{% from 'components/macros.html' import alert, card_header, user_info, action_buttons, pagination, empty_state %}

{% block page_content %}

{# Show success message #}
{% if success %}
    {{ alert(success, 'success') }}
{% endif %}

{# User list card #}
<div class="card shadow-sm">
    {{ card_header(
        'Users',
        icon='people',
        badge_text=users|length,
        action_button={
            'text': 'Add User',
            'icon': 'plus-circle',
            'modal': 'createUserModal'
        }
    ) }}

    <div class="card-body p-0">
        {% if users %}
        <table class="table mb-0">
            <thead>
                <tr>
                    <th>User</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user_info(user) }}</td>
                    <td>
                        {{ action_buttons(
                            view_url=url_for('users.detail', user_id=user.id),
                            edit_url=url_for('users.edit', user_id=user.id),
                            delete_url=url_for('users.delete', user_id=user.id)
                        ) }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
            {{ empty_state(
                icon='person-plus',
                title='No users yet',
                message='Get started by creating your first user',
                action_text='Create User',
                action_url='/users/create'
            ) }}
        {% endif %}
    </div>

    {# Pagination #}
    <div class="card-footer">
        {{ pagination(current_page=page, total_pages=total_pages, base_url='/users') }}
    </div>
</div>

{% endblock %}
```

---

## Best Practices

1. **Import Only What You Need**: Import specific macros rather than all of them
   ```jinja2
   {% from 'components/macros.html' import avatar_circle, alert %}
   ```

2. **Consistent Styling**: Use macros to maintain consistent UI across all pages

3. **Customize When Needed**: Override default parameters for specific use cases
   ```jinja2
   {{ avatar_circle(user.name, size='60px', bg_color='success') }}
   ```

4. **Combine Macros**: Macros can be used together for complex components
   ```jinja2
   <div class="d-flex align-items-center">
       {{ avatar_circle(user.name) }}
       <div class="ms-2">
           {{ status_badge(user.is_active) }}
       </div>
   </div>
   ```

5. **Keep DRY**: If you find yourself repeating HTML patterns, create a new macro

---

## Adding New Macros

To add a new macro to `components/macros.html`:

1. Define the macro with descriptive parameters:
   ```jinja2
   {% macro my_component(param1, param2='default') %}
       <div class="my-component">
           {{ param1 }} - {{ param2 }}
       </div>
   {% endmacro %}
   ```

2. Document it in this README

3. Test it in a template

4. Share with the team!

---

**Last Updated**: 2025-10-24
**Version**: 1.0
