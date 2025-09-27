import streamlit as st
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

def load_applications():
    """Load job applications from JSON file"""
    if os.path.exists('job_applications.json'):
        with open('job_applications.json', 'r') as f:
            return json.load(f)
    return []

def save_applications(applications):
    """Save job applications to JSON file"""
    with open('job_applications.json', 'w') as f:
        json.dump(applications, f, indent=2)

def add_autofocus_script():
    """Add JavaScript for autofocus functionality"""
    autofocus_script = """
    <script>
    function setupAutofocus() {
        setTimeout(function() {
            const inputs = document.querySelectorAll('input[type="text"]');
            if (inputs.length > 0) {
                inputs[0].focus();
            }

            inputs.forEach((input, index) => {
                input.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        if (index < inputs.length - 1) {
                            inputs[index + 1].focus();
                        } else {
                            // Focus on submit button or trigger form submission
                            const submitButton = document.querySelector('button[kind="primary"]');
                            if (submitButton) {
                                submitButton.click();
                            }
                        }
                    }
                });
            });
        }, 100);
    }

    // Run setup when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupAutofocus);
    } else {
        setupAutofocus();
    }

    // Re-run setup after Streamlit updates
    const observer = new MutationObserver(function(mutations) {
        setupAutofocus();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """
    components.html(autofocus_script, height=0)

def main():
    st.set_page_config(page_title="Job Application Tracker", page_icon="💼")

    st.title("💼 Job Application Tracker")

    # Add autofocus functionality
    add_autofocus_script()

    # Load existing applications
    applications = load_applications()

    # Form for adding new application
    st.header("Add New Application")

    with st.form("job_application_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            company = st.text_input("Company", key="company")

        with col2:
            job_role = st.text_input("Job Role", key="job_role")

        col3, col4, col5 = st.columns(3)

        with col3:
            location = st.text_input("Location", key="location")

        with col4:
            source = st.text_input("Source", key="source")

        with col5:
            status = st.selectbox("Status",
                                ["Applied", "Interview Scheduled", "In Progress",
                                 "Rejected", "Offer Received", "Withdrawn"],
                                key="status")

        submitted = st.form_submit_button("Add Application", use_container_width=True)

        if submitted and company and job_role:
            new_application = {
                "id": len(applications) + 1,
                "company": company,
                "job_role": job_role,
                "status": status,
                "date_applied": datetime.now().strftime("%Y-%m-%d"),
                "location": location or "Not specified",
                "source": source or "Not specified"
            }
            applications.append(new_application)
            save_applications(applications)
            st.success(f"Added application for {job_role} at {company}!")
            st.rerun()
        elif submitted:
            st.error("Please fill in both Company and Job Role fields.")

    # Display existing applications
    if applications:
        st.header("Your Applications")

        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_company = st.text_input("Filter by Company", key="filter_company")
        with col2:
            filter_location = st.text_input("Filter by Location", key="filter_location")
        with col3:
            filter_status = st.selectbox("Filter by Status",
                                       ["All"] + ["Applied", "Interview Scheduled", "In Progress",
                                                  "Rejected", "Offer Received", "Withdrawn"],
                                       key="filter_status")

        # Filter applications
        filtered_apps = applications
        if filter_company:
            filtered_apps = [app for app in filtered_apps if filter_company.lower() in app["company"].lower()]
        if filter_location:
            filtered_apps = [app for app in filtered_apps if filter_location.lower() in app.get("location", "").lower()]
        if filter_status != "All":
            filtered_apps = [app for app in filtered_apps if app["status"] == filter_status]

        # Display applications in a table
        if filtered_apps:
            for app in reversed(filtered_apps):  # Show newest first
                with st.expander(f"{app['company']} - {app['job_role']} ({app['status']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Company:** {app['company']}")
                        st.write(f"**Role:** {app['job_role']}")
                        st.write(f"**Location:** {app.get('location', 'Not specified')}")
                    with col2:
                        st.write(f"**Status:** {app['status']}")
                        st.write(f"**Applied:** {app['date_applied']}")
                        st.write(f"**Source:** {app.get('source', 'Not specified')}")

                    # Option to update status
                    new_status = st.selectbox(f"Update Status",
                                            ["Applied", "Interview Scheduled", "In Progress",
                                             "Rejected", "Offer Received", "Withdrawn"],
                                            index=["Applied", "Interview Scheduled", "In Progress",
                                                   "Rejected", "Offer Received", "Withdrawn"].index(app['status']),
                                            key=f"update_status_{app['id']}")

                    if st.button(f"Update Status", key=f"update_btn_{app['id']}"):
                        # Update the status in applications list
                        for i, a in enumerate(applications):
                            if a['id'] == app['id']:
                                applications[i]['status'] = new_status
                                break
                        save_applications(applications)
                        st.success(f"Updated status for {app['company']} - {app['job_role']}")
                        st.rerun()
        else:
            st.info("No applications match your filters.")

        # Summary statistics
        st.header("Summary")
        status_counts = {}
        for app in applications:
            status_counts[app['status']] = status_counts.get(app['status'], 0) + 1

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Applications", len(applications))
        with col2:
            st.metric("Pending", status_counts.get("Applied", 0) + status_counts.get("In Progress", 0))
        with col3:
            st.metric("Offers Received", status_counts.get("Offer Received", 0))

        # Status breakdown
        st.subheader("Status Breakdown")
        for status, count in status_counts.items():
            st.write(f"• **{status}:** {count}")

    else:
        st.info("No job applications recorded yet. Add your first application above!")

if __name__ == "__main__":
    main()