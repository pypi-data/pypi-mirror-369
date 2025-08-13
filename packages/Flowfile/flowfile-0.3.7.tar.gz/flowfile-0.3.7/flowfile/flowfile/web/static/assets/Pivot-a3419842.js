import { d as defineComponent, l as computed, c as openBlock, h as createBlock, w as withCtx, f as createVNode, u as unref, ap as ElIcon, p as createBaseVNode, e as createElementBlock, i as createCommentVNode, aq as ElPopover, _ as _export_sfc, r as ref, n as onMounted, R as nextTick, o as onUnmounted, b as resolveComponent, F as Fragment, q as renderList, s as normalizeClass, v as withModifiers, t as toDisplayString, a7 as Teleport } from "./index-f6c15e76.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { C as ContextMenu, S as SettingsSection } from "./SettingsSection-4c0f45f5.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1$2 = { class: "validation-wrapper" };
const _hoisted_2$1 = {
  key: 0,
  class: "error-message"
};
const _hoisted_3$1 = {
  key: 1,
  class: "error-message"
};
const _hoisted_4$1 = {
  key: 2,
  class: "error-message"
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "PivotValidation",
  props: {
    pivotInput: {}
  },
  setup(__props) {
    const props = __props;
    const showValidationMessages = computed(() => {
      return !props.pivotInput.pivot_column || !props.pivotInput.value_col || props.pivotInput.aggregations.length === 0;
    });
    return (_ctx, _cache) => {
      return showValidationMessages.value ? (openBlock(), createBlock(unref(ElPopover), {
        key: 0,
        placement: "top",
        width: "200",
        trigger: "hover",
        content: "Some required fields are missing"
      }, {
        reference: withCtx(() => [
          createVNode(unref(ElIcon), {
            color: "#FF6B6B",
            class: "warning-icon"
          }, {
            default: withCtx(() => _cache[0] || (_cache[0] = [
              createBaseVNode("i", { class: "el-icon-warning" }, null, -1)
            ])),
            _: 1,
            __: [0]
          })
        ]),
        default: withCtx(() => [
          createBaseVNode("div", _hoisted_1$2, [
            !_ctx.pivotInput.pivot_column ? (openBlock(), createElementBlock("p", _hoisted_2$1, "Pivot Column cannot be empty.")) : createCommentVNode("", true),
            !_ctx.pivotInput.value_col ? (openBlock(), createElementBlock("p", _hoisted_3$1, "Value Column cannot be empty.")) : createCommentVNode("", true),
            _ctx.pivotInput.aggregations.length === 0 ? (openBlock(), createElementBlock("p", _hoisted_4$1, " At least one aggregation must be selected. ")) : createCommentVNode("", true)
          ])
        ]),
        _: 1
      })) : createCommentVNode("", true);
    };
  }
});
const PivotValidation_vue_vue_type_style_index_0_scoped_3eb585b2_lang = "";
const PivotValidation = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-3eb585b2"]]);
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { class: "listbox" };
const _hoisted_4 = ["onClick", "onContextmenu", "onDragstart", "onDrop"];
const _hoisted_5 = { class: "listbox-wrapper" };
const _hoisted_6 = { class: "list-wrapper" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "pivot",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const showContextMenu = ref(false);
    const dataLoaded = ref(false);
    const contextMenuPosition = ref({ x: 0, y: 0 });
    const selectedColumns = ref([]);
    const contextMenuOptions = ref([]);
    const contextMenuRef = ref(null);
    const nodeData = ref(null);
    const draggedColumnName = ref(null);
    const aggOptions = [
      "sum",
      "count",
      "min",
      "max",
      "n_unique",
      "mean",
      "median",
      "first",
      "last",
      "concat"
    ];
    const pivotInput = ref({
      index_columns: [],
      pivot_column: null,
      value_col: null,
      aggregations: []
    });
    const nodePivot = ref(null);
    const singleColumnSelected = computed(() => selectedColumns.value.length === 1);
    const getColumnClass = (columnName) => {
      return selectedColumns.value.includes(columnName) ? "is-selected" : "";
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
    const onDropInSection = (section) => {
      if (draggedColumnName.value) {
        removeColumnIfExists(draggedColumnName.value);
        if (section === "index" && !pivotInput.value.index_columns.includes(draggedColumnName.value)) {
          pivotInput.value.index_columns.push(draggedColumnName.value);
        } else if (section === "pivot") {
          pivotInput.value.pivot_column = draggedColumnName.value;
        } else if (section === "value") {
          pivotInput.value.value_col = draggedColumnName.value;
        }
        draggedColumnName.value = null;
      }
    };
    const openContextMenu = (columnName, event) => {
      selectedColumns.value = [columnName];
      contextMenuPosition.value = { x: event.clientX, y: event.clientY };
      contextMenuOptions.value = [
        {
          label: "Add to Index",
          action: "index",
          disabled: isColumnAssigned(columnName)
        },
        {
          label: "Set as Pivot",
          action: "pivot",
          disabled: isColumnAssigned(columnName) || !singleColumnSelected.value
        },
        {
          label: "Set as Value",
          action: "value",
          disabled: isColumnAssigned(columnName) || !singleColumnSelected.value
        }
      ];
      showContextMenu.value = true;
    };
    const handleContextMenuSelect = (action) => {
      const column = selectedColumns.value[0];
      if (action === "index" && !pivotInput.value.index_columns.includes(column)) {
        removeColumnIfExists(column);
        pivotInput.value.index_columns.push(column);
      } else if (action === "pivot") {
        removeColumnIfExists(column);
        pivotInput.value.pivot_column = column;
      } else if (action === "value") {
        removeColumnIfExists(column);
        pivotInput.value.value_col = column;
      }
      closeContextMenu();
    };
    const isColumnAssigned = (columnName) => {
      return pivotInput.value.index_columns.includes(columnName) || pivotInput.value.pivot_column === columnName || pivotInput.value.value_col === columnName;
    };
    const removeColumnIfExists = (column) => {
      pivotInput.value.index_columns = pivotInput.value.index_columns.filter((col) => col !== column);
      if (pivotInput.value.pivot_column === column)
        pivotInput.value.pivot_column = null;
      if (pivotInput.value.value_col === column)
        pivotInput.value.value_col = null;
    };
    const removeColumn = (type, column) => {
      if (type === "index") {
        pivotInput.value.index_columns = pivotInput.value.index_columns.filter((col) => col !== column);
      } else if (type === "pivot") {
        pivotInput.value.pivot_column = null;
      } else if (type === "value") {
        pivotInput.value.value_col = null;
      }
    };
    const handleItemClick = (columnName) => {
      selectedColumns.value = [columnName];
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodePivot.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      if (nodeData.value) {
        if (nodePivot.value) {
          if (nodePivot.value.pivot_input) {
            pivotInput.value = nodePivot.value.pivot_input;
          } else {
            nodePivot.value.pivot_input = pivotInput.value;
          }
        }
      }
      dataLoaded.value = true;
      nodeStore.isDrawerOpen = true;
    };
    const handleClickOutside = (event) => {
      const targetEvent = event.target;
      if (targetEvent.id === "pivot-context-menu")
        return;
      showContextMenu.value = false;
    };
    const closeContextMenu = () => {
      showContextMenu.value = false;
    };
    const pushNodeData = async () => {
      if (pivotInput.value) {
        nodeStore.updateSettings(nodePivot);
      }
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
      const _component_el_option = resolveComponent("el-option");
      const _component_el_select = resolveComponent("el-select");
      return dataLoaded.value && nodePivot.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodePivot.value,
          "onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => nodePivot.value = $event)
        }, {
          default: withCtx(() => {
            var _a, _b;
            return [
              createBaseVNode("div", _hoisted_2, [
                createBaseVNode("ul", _hoisted_3, [
                  (openBlock(true), createElementBlock(Fragment, null, renderList((_b = (_a = nodeData.value) == null ? void 0 : _a.main_input) == null ? void 0 : _b.table_schema, (col_schema, index) => {
                    return openBlock(), createElementBlock("li", {
                      key: col_schema.name,
                      class: normalizeClass(getColumnClass(col_schema.name)),
                      draggable: "true",
                      onClick: ($event) => handleItemClick(col_schema.name),
                      onContextmenu: withModifiers(($event) => openContextMenu(col_schema.name, $event), ["prevent"]),
                      onDragstart: ($event) => onDragStart(col_schema.name, $event),
                      onDragover: _cache[0] || (_cache[0] = withModifiers(() => {
                      }, ["prevent"])),
                      onDrop: ($event) => onDrop(index)
                    }, toDisplayString(col_schema.name) + " (" + toDisplayString(col_schema.data_type) + ") ", 43, _hoisted_4);
                  }), 128))
                ])
              ]),
              showContextMenu.value ? (openBlock(), createBlock(ContextMenu, {
                key: 0,
                id: "pivot-context-menu",
                ref_key: "contextMenuRef",
                ref: contextMenuRef,
                position: contextMenuPosition.value,
                options: contextMenuOptions.value,
                onSelect: handleContextMenuSelect,
                onClose: closeContextMenu
              }, null, 8, ["position", "options"])) : createCommentVNode("", true),
              createBaseVNode("div", _hoisted_5, [
                createVNode(SettingsSection, {
                  title: "Index Keys",
                  items: pivotInput.value.index_columns,
                  droppable: "true",
                  onRemoveItem: _cache[1] || (_cache[1] = ($event) => removeColumn("index", $event)),
                  onDragover: _cache[2] || (_cache[2] = withModifiers(() => {
                  }, ["prevent"])),
                  onDrop: _cache[3] || (_cache[3] = ($event) => onDropInSection("index"))
                }, null, 8, ["items"]),
                createVNode(SettingsSection, {
                  title: "Pivot Column",
                  items: [pivotInput.value.pivot_column ?? ""],
                  droppable: "true",
                  onRemoveItem: _cache[4] || (_cache[4] = ($event) => removeColumn("pivot", $event)),
                  onDragover: _cache[5] || (_cache[5] = withModifiers(() => {
                  }, ["prevent"])),
                  onDrop: _cache[6] || (_cache[6] = ($event) => onDropInSection("pivot"))
                }, null, 8, ["items"]),
                createVNode(SettingsSection, {
                  title: "Value Column",
                  items: [pivotInput.value.value_col ?? ""],
                  droppable: "true",
                  onRemoveItem: _cache[7] || (_cache[7] = ($event) => removeColumn("value", $event)),
                  onDragover: _cache[8] || (_cache[8] = withModifiers(() => {
                  }, ["prevent"])),
                  onDrop: _cache[9] || (_cache[9] = ($event) => onDropInSection("value"))
                }, null, 8, ["items"]),
                createBaseVNode("div", _hoisted_6, [
                  _cache[12] || (_cache[12] = createBaseVNode("div", { class: "listbox-subtitle" }, "Select aggregations", -1)),
                  createVNode(_component_el_select, {
                    modelValue: pivotInput.value.aggregations,
                    "onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => pivotInput.value.aggregations = $event),
                    multiple: "",
                    placeholder: "Select",
                    size: "small",
                    style: { "width": "100%" }
                  }, {
                    default: withCtx(() => [
                      (openBlock(), createElementBlock(Fragment, null, renderList(aggOptions, (item) => {
                        return createVNode(_component_el_option, {
                          key: item,
                          label: item,
                          value: item,
                          style: { "width": "400px" }
                        }, null, 8, ["label", "value"]);
                      }), 64))
                    ]),
                    _: 1
                  }, 8, ["modelValue"])
                ]),
                createVNode(PivotValidation, { "pivot-input": pivotInput.value }, null, 8, ["pivot-input"])
              ])
            ];
          }),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const pivot_vue_vue_type_style_index_0_scoped_d0f14439_lang = "";
const readInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-d0f14439"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Pivot",
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
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      drawer.value = false;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
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
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "pivot.png",
          title: `${__props.nodeId}: Pivot data`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Pivot data",
            intro: "Pivot rows to columns, to understand your data better"
          }),
          createVNode(readInput, {
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
