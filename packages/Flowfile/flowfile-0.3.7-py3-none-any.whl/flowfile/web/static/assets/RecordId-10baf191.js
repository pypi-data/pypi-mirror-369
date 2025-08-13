import { d as defineComponent, r as ref, n as onMounted, R as nextTick, o as onUnmounted, b as resolveComponent, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, g as createTextVNode, a5 as withDirectives, a6 as vModelText, F as Fragment, q as renderList, s as normalizeClass, v as withModifiers, t as toDisplayString, h as createBlock, i as createCommentVNode, a7 as Teleport } from "./index-f6c15e76.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { C as ContextMenu, S as SettingsSection } from "./SettingsSection-4c0f45f5.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { class: "listbox-wrapper" };
const _hoisted_4 = { key: 0 };
const _hoisted_5 = { class: "listbox" };
const _hoisted_6 = { class: "column-options" };
const _hoisted_7 = ["onClick", "onContextmenu", "onDragstart", "onDrop"];
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "recordId",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const showContextMenu = ref(false);
    const contextMenuPosition = ref({ x: 0, y: 0 });
    const dataLoaded = ref(false);
    const contextMenuRef = ref(null);
    const nodeRecordId = ref(null);
    const nodeData = ref(null);
    const contextMenuOptions = ref([]);
    const draggedColumnName = ref(null);
    const selectedColumns = ref([]);
    const getColumnClass = (columnName) => {
      return selectedColumns.value.includes(columnName) ? "is-selected" : "";
    };
    const onDropInSection = (section) => {
      var _a, _b;
      if (draggedColumnName.value) {
        if (section === "add" && !((_a = nodeRecordId.value) == null ? void 0 : _a.record_id_input.group_by_columns.includes(draggedColumnName.value))) {
          (_b = nodeRecordId.value) == null ? void 0 : _b.record_id_input.group_by_columns.push(draggedColumnName.value);
        }
        draggedColumnName.value = null;
      }
    };
    const closeContextMenu = () => {
      showContextMenu.value = false;
    };
    const handleItemClick = (columnName) => {
      selectedColumns.value = [columnName];
    };
    const loadNodeData = async (nodeId) => {
      var _a, _b, _c;
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodeRecordId.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      if (!((_b = nodeData.value) == null ? void 0 : _b.setting_input.is_setup) && nodeRecordId.value) {
        nodeRecordId.value.record_id_input = {
          offset: 1,
          output_column_name: "record_id",
          group_by: false,
          group_by_columns: []
        };
      }
      dataLoaded.value = true;
      if ((_c = nodeRecordId.value) == null ? void 0 : _c.is_setup) {
        nodeRecordId.value.is_setup = true;
      }
    };
    const onDragStart = (columnName, event) => {
      var _a;
      draggedColumnName.value = columnName;
      (_a = event.dataTransfer) == null ? void 0 : _a.setData("text/plain", columnName);
    };
    const onDrop = (index) => {
      var _a, _b;
      if (draggedColumnName.value) {
        const colSchema = (_b = (_a = nodeData.value) == null ? void 0 : _a.main_input) == null ? void 0 : _b.table_schema;
        if (colSchema) {
          const fromIndex = colSchema.findIndex((col) => col.name === draggedColumnName.value);
          if (fromIndex !== -1 && fromIndex !== index) {
            const [movedColumn] = colSchema.splice(fromIndex, 1);
            colSchema.splice(index, 0, movedColumn);
          }
        }
        draggedColumnName.value = null;
      }
    };
    const openContextMenu = (columnName, event) => {
      selectedColumns.value = [columnName];
      contextMenuPosition.value = { x: event.clientX, y: event.clientY };
      contextMenuOptions.value = [
        {
          label: "Group by",
          action: "add",
          disabled: isColumnAssigned(columnName)
        }
      ];
      showContextMenu.value = true;
    };
    const handleClickOutside = (event) => {
      var _a;
      if (!((_a = contextMenuRef.value) == null ? void 0 : _a.contains(event.target))) {
        showContextMenu.value = false;
      }
    };
    const isColumnAssigned = (columnName) => {
      if (nodeRecordId.value) {
        return nodeRecordId.value.record_id_input.group_by_columns.includes(columnName);
      }
      return false;
    };
    const handleContextMenuSelect = (action) => {
      const nodeRecord = nodeRecordId.value;
      if (nodeRecord && action === "add") {
        selectedColumns.value.filter((col) => !isColumnAssigned(col)).forEach((col) => {
          nodeRecord.record_id_input.group_by_columns.push(col);
        });
      }
    };
    const removeColumn = (type, column) => {
      if (nodeRecordId.value) {
        if (type === "add") {
          nodeRecordId.value.record_id_input.group_by_columns = nodeRecordId.value.record_id_input.group_by_columns.filter((col) => col !== column);
        }
      }
    };
    const pushNodeData = async () => {
      nodeStore.updateSettings(nodeRecordId);
      dataLoaded.value = false;
      nodeStore.isDrawerOpen = false;
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    onMounted(async () => {
      await nextTick();
      window.addEventListener("click", handleClickOutside);
    });
    onUnmounted(() => {
      window.removeEventListener("click", handleClickOutside);
    });
    return (_ctx, _cache) => {
      const _component_el_col = resolveComponent("el-col");
      const _component_el_row = resolveComponent("el-row");
      const _component_el_checkbox = resolveComponent("el-checkbox");
      return dataLoaded.value && nodeRecordId.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeRecordId.value,
          "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => nodeRecordId.value = $event)
        }, {
          default: withCtx(() => {
            var _a, _b;
            return [
              createBaseVNode("div", _hoisted_2, [
                _cache[10] || (_cache[10] = createBaseVNode("div", { class: "listbox-subtitle" }, "Settings", -1)),
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, {
                      span: 10,
                      class: "grid-content"
                    }, {
                      default: withCtx(() => _cache[8] || (_cache[8] = [
                        createTextVNode("Offset")
                      ])),
                      _: 1,
                      __: [8]
                    }),
                    createVNode(_component_el_col, {
                      span: 8,
                      class: "grid-content"
                    }, {
                      default: withCtx(() => [
                        withDirectives(createBaseVNode("input", {
                          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => nodeRecordId.value.record_id_input.offset = $event),
                          type: "number",
                          min: "0",
                          step: "1"
                        }, null, 512), [
                          [vModelText, nodeRecordId.value.record_id_input.offset]
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                }),
                createVNode(_component_el_row, null, {
                  default: withCtx(() => [
                    createVNode(_component_el_col, {
                      span: 10,
                      class: "grid-content"
                    }, {
                      default: withCtx(() => _cache[9] || (_cache[9] = [
                        createTextVNode("Output name")
                      ])),
                      _: 1,
                      __: [9]
                    }),
                    createVNode(_component_el_col, {
                      span: 8,
                      class: "grid-content"
                    }, {
                      default: withCtx(() => [
                        withDirectives(createBaseVNode("input", {
                          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeRecordId.value.record_id_input.output_column_name = $event),
                          type: "text"
                        }, null, 512), [
                          [vModelText, nodeRecordId.value.record_id_input.output_column_name]
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ]),
              createBaseVNode("div", _hoisted_3, [
                createVNode(_component_el_checkbox, {
                  modelValue: nodeRecordId.value.record_id_input.group_by,
                  "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => nodeRecordId.value.record_id_input.group_by = $event),
                  label: "Assign record id by group",
                  size: "large"
                }, null, 8, ["modelValue"]),
                nodeRecordId.value.record_id_input.group_by ? (openBlock(), createElementBlock("div", _hoisted_4, [
                  _cache[11] || (_cache[11] = createBaseVNode("div", { class: "listbox-subtitle" }, "Optional Settings", -1)),
                  createBaseVNode("ul", _hoisted_5, [
                    createBaseVNode("div", _hoisted_6, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList((_b = (_a = nodeData.value) == null ? void 0 : _a.main_input) == null ? void 0 : _b.table_schema, (col_schema, index) => {
                        return openBlock(), createElementBlock("li", {
                          key: col_schema.name,
                          class: normalizeClass(getColumnClass(col_schema.name)),
                          draggable: "true",
                          onClick: ($event) => handleItemClick(col_schema.name),
                          onContextmenu: withModifiers(($event) => openContextMenu(col_schema.name, $event), ["prevent"]),
                          onDragstart: ($event) => onDragStart(col_schema.name, $event),
                          onDragover: _cache[3] || (_cache[3] = withModifiers(() => {
                          }, ["prevent"])),
                          onDrop: ($event) => onDrop(index)
                        }, toDisplayString(col_schema.name) + " (" + toDisplayString(col_schema.data_type) + ") ", 43, _hoisted_7);
                      }), 128))
                    ]),
                    showContextMenu.value ? (openBlock(), createBlock(ContextMenu, {
                      key: 0,
                      id: "record-id-menu",
                      ref_key: "contextMenuRef",
                      ref: contextMenuRef,
                      position: contextMenuPosition.value,
                      options: contextMenuOptions.value,
                      onSelect: handleContextMenuSelect,
                      onClose: closeContextMenu
                    }, null, 8, ["position", "options"])) : createCommentVNode("", true),
                    createVNode(SettingsSection, {
                      title: "Group by columns",
                      items: nodeRecordId.value.record_id_input.group_by_columns,
                      droppable: "true",
                      onRemoveItem: _cache[4] || (_cache[4] = ($event) => removeColumn("add", $event)),
                      onDragover: _cache[5] || (_cache[5] = withModifiers(() => {
                      }, ["prevent"])),
                      onDrop: _cache[6] || (_cache[6] = ($event) => onDropInSection("add"))
                    }, null, 8, ["items"])
                  ])
                ])) : createCommentVNode("", true)
              ])
            ];
          }),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "RecordId",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const childComp = ref(null);
    const props = __props;
    const el = ref(null);
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
      drawer.value = false;
      nodeStore.isDrawerOpen = false;
    };
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      nodeStore.closeDrawer();
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        return;
      }
      if (childComp.value) {
        childComp.value.loadNodeData(props.nodeId);
        nodeStore.openDrawer(closeOnDrawer);
      }
    };
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        ref_key: "el",
        ref: el
      }, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "record_id.png",
          title: `${__props.nodeId}: Add record Id`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Add record Id",
            intro: "<p>\n    <strong>Record ID:</strong> This is a unique number or identifier for each entry in our database, like a personal ID number that ensures every record is distinct.<br><br>\n    <strong>Offset:</strong> Think of this as the starting point or position where a record is found. It's like telling you on which page to find a word in a book.<br><br>\n    <strong>Column Name:</strong> This is the name of the category or type of information stored in each column, similar to how a label on a box tells you what's inside.</p>"
          }),
          createVNode(_sfc_main$1, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ], 512);
    };
  }
});
export {
  _sfc_main as default
};
