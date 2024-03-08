special_filter_feature = {
  onload: function (listview) {
    //Copy/paste from erpnext/projects/doctype/task/task_list.js because listview_settings
    // do not execute standard call and after custom app call
    // The only way is to rewrite the standard method
    let method = "erpnext.projects.doctype.task.task.set_multiple_status";

    listview.page.add_menu_item(__("Set as Open"), function () {
      listview.call_for_selected_items(method, {"status": "Open"});
    });

    listview.page.add_menu_item(__("Set as Completed"), function () {
      listview.call_for_selected_items(method, {"status": "Completed"});
    });
    //End of copy/paste

    //Purpose of this custom JS : add a spécial filter button on the list
    listview.page.add_inner_button(__('Special Filter Parent Task'), () => {
      dialog_filter_parent_task(listview);
    }, '');

  },
};

$.extend(frappe.listview_settings['Task'], special_filter_feature);

function dialog_filter_parent_task(listview) {

  let d = new frappe.ui.Dialog({
    title: 'Filter On Parent Task By Project',
    fields: [
      {
        label: __('Project'),
        fieldname: 'project_filter',
        fieldtype: 'Link',
        options: "Project",
        default: listview.page.fields_dict.project.get_value(),
        change: function () {
          set_query_filter(this.get_value());
        },
      },
      {
        label: __('Parent Task'),
        fieldname: 'task_filter',
        fieldtype: 'Link',
        options: "Task",
      },
    ],
    size: 'small', // small, large, extra-large
    primary_action_label: __('Apply Filter'),
    primary_action(values) {
      listview.filter_area.remove("project").then(() => {
        listview.filter_area.add("Task", "project", "=", d.fields_dict.project_filter.get_value());
      });
      listview.filter_area.remove("parent_task").then(() => {
        listview.filter_area.add("Task", "parent_task", "=", d.fields_dict.task_filter.get_value());
      });
      d.hide();
    }
  });
  d.show();
  set_query_filter(d.fields_dict.project_filter.get_value());

  function set_query_filter(prj) {
    d.fields_dict.task_filter.get_query = {
      "filters": {"is_group": 1, "project": prj}
    };
  }
}
