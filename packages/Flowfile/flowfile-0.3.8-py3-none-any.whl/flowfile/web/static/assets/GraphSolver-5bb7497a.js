import { d as defineComponent, c as openBlock, e as createElementBlock, p as createBaseVNode, F as Fragment, q as renderList, s as normalizeClass, t as toDisplayString, T as normalizeStyle, _ as _export_sfc, g as createTextVNode, i as createCommentVNode, r as ref, l as computed, n as onMounted, R as nextTick, o as onUnmounted, b as resolveComponent, f as createVNode, w as withCtx, v as withModifiers, h as createBlock, a7 as Teleport } from "./index-f6c15e76.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1$3 = ["onClick"];
const _sfc_main$3 = /* @__PURE__ */ defineComponent({
  __name: "ContextMenu",
  props: {
    position: { type: Object, required: true },
    options: {
      type: Array,
      required: true
    }
  },
  emits: ["select", "close"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const selectOption = (action) => {
      emit("select", action);
      emit("close");
    };
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        class: "context-menu",
        style: normalizeStyle({ top: __props.position.y + "px", left: __props.position.x + "px" })
      }, [
        createBaseVNode("ul", null, [
          (openBlock(true), createElementBlock(Fragment, null, renderList(__props.options, (option) => {
            return openBlock(), createElementBlock("li", {
              key: option.action,
              class: normalizeClass({ disabled: option.disabled }),
              onClick: ($event) => !option.disabled && selectOption(option.action)
            }, toDisplayString(option.label), 11, _hoisted_1$3);
          }), 128))
        ])
      ], 4);
    };
  }
});
const ContextMenu_vue_vue_type_style_index_0_scoped_d0286fd2_lang = "";
const ContextMenu = /* @__PURE__ */ _export_sfc(_sfc_main$3, [["__scopeId", "data-v-d0286fd2"]]);
const _hoisted_1$2 = { class: "listbox-wrapper" };
const _hoisted_2$1 = { class: "listbox-row" };
const _hoisted_3$1 = { class: "listbox-subtitle" };
const _hoisted_4$1 = { class: "items-container" };
const _hoisted_5$1 = {
  key: 0,
  class: "item-box"
};
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "SettingsSection",
  props: {
    title: { type: String, required: true },
    item: { type: String, required: true }
    // Changed to a single item
  },
  emits: ["removeItem"],
  setup(__props, { emit: __emit }) {
    const emit = __emit;
    const emitRemove = (item) => {
      emit("removeItem", item);
    };
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$2, [
        createBaseVNode("div", _hoisted_2$1, [
          createBaseVNode("div", _hoisted_3$1, toDisplayString(__props.title), 1),
          createBaseVNode("div", _hoisted_4$1, [
            __props.item !== "" ? (openBlock(), createElementBlock("div", _hoisted_5$1, [
              createTextVNode(toDisplayString(__props.item) + " ", 1),
              createBaseVNode("span", {
                class: "remove-btn",
                onClick: _cache[0] || (_cache[0] = ($event) => emitRemove(__props.item))
              }, "x")
            ])) : createCommentVNode("", true)
          ])
        ])
      ]);
    };
  }
});
const SettingsSection_vue_vue_type_style_index_0_scoped_43acf78a_lang = "";
const SettingsSection = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-43acf78a"]]);
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { class: "listbox" };
const _hoisted_4 = ["onClick", "onContextmenu", "onDragstart", "onDrop"];
const _hoisted_5 = { class: "listbox-wrapper" };
const _hoisted_6 = { class: "listbox-wrapper" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "graphSolver",
  props: { nodeId: { type: Number, required: true } },
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
    const graphSolverInput = ref({
      col_from: "",
      col_to: "",
      output_column_name: "group_column"
    });
    const nodeGraphSolver = ref(null);
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
        if (section === "from" && graphSolverInput.value.col_from !== draggedColumnName.value) {
          graphSolverInput.value.col_from = draggedColumnName.value;
        } else if (section === "to") {
          graphSolverInput.value.col_to = draggedColumnName.value;
        }
        draggedColumnName.value = null;
      }
    };
    const openContextMenu = (columnName, event) => {
      selectedColumns.value = [columnName];
      contextMenuPosition.value = { x: event.clientX, y: event.clientY };
      contextMenuOptions.value = [
        {
          label: "Assign as From",
          action: "from",
          disabled: isColumnAssigned(columnName) || !singleColumnSelected.value
        },
        {
          label: "Assign as To",
          action: "to",
          disabled: isColumnAssigned(columnName) || !singleColumnSelected.value
        }
      ];
      showContextMenu.value = true;
    };
    const handleContextMenuSelect = (action) => {
      const column = selectedColumns.value[0];
      if (action === "from" && graphSolverInput.value.col_from !== column) {
        removeColumnIfExists(column);
        graphSolverInput.value.col_from = column;
      } else if (action === "to") {
        removeColumnIfExists(column);
        graphSolverInput.value.col_to = column;
      }
      closeContextMenu();
    };
    const isColumnAssigned = (columnName) => {
      return graphSolverInput.value.col_from === columnName || graphSolverInput.value.col_to === columnName;
    };
    const removeColumnIfExists = (columnName) => {
      if (graphSolverInput.value.col_from === columnName) {
        graphSolverInput.value.col_from = "";
      } else if (graphSolverInput.value.col_to === columnName) {
        graphSolverInput.value.col_to = "";
      }
    };
    const removeColumn = (type, _) => {
      if (type === "from") {
        graphSolverInput.value.col_from = "";
      } else if (type === "to") {
        graphSolverInput.value.col_to = "";
      }
    };
    const handleItemClick = (columnName) => {
      selectedColumns.value = [columnName];
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      console.log("loadNodeData from groupby");
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodeGraphSolver.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      if (nodeData.value) {
        if (nodeGraphSolver.value) {
          if (nodeGraphSolver.value.graph_solver_input) {
            graphSolverInput.value = nodeGraphSolver.value.graph_solver_input;
          } else {
            nodeGraphSolver.value.graph_solver_input = graphSolverInput.value;
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
      if (nodeGraphSolver.value) {
        nodeStore.updateSettings(nodeGraphSolver);
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
      const _component_el_input = resolveComponent("el-input");
      return dataLoaded.value && nodeGraphSolver.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeGraphSolver.value,
          "onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => nodeGraphSolver.value = $event)
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
                  title: "From Column",
                  item: graphSolverInput.value.col_from ?? "",
                  droppable: "true",
                  onRemoveItem: _cache[1] || (_cache[1] = ($event) => removeColumn("from", $event)),
                  onDragover: _cache[2] || (_cache[2] = withModifiers(() => {
                  }, ["prevent"])),
                  onDrop: _cache[3] || (_cache[3] = ($event) => onDropInSection("from"))
                }, null, 8, ["item"]),
                createVNode(SettingsSection, {
                  title: "To Column",
                  item: graphSolverInput.value.col_to ?? "",
                  droppable: "true",
                  onRemoveItem: _cache[4] || (_cache[4] = ($event) => removeColumn("to", $event)),
                  onDragover: _cache[5] || (_cache[5] = withModifiers(() => {
                  }, ["prevent"])),
                  onDrop: _cache[6] || (_cache[6] = ($event) => onDropInSection("to"))
                }, null, 8, ["item"]),
                createBaseVNode("div", _hoisted_6, [
                  _cache[9] || (_cache[9] = createBaseVNode("div", { class: "listbox-subtitle" }, "Select Output column name", -1)),
                  createVNode(_component_el_input, {
                    modelValue: graphSolverInput.value.output_column_name,
                    "onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => graphSolverInput.value.output_column_name = $event),
                    style: { "width": "240px" },
                    placeholder: "Please input"
                  }, null, 8, ["modelValue"])
                ])
              ])
            ];
          }),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const graphSolver_vue_vue_type_style_index_0_scoped_5a467b52_lang = "";
const readInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-5a467b52"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "GraphSolver",
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
        nodeStore.openDrawer(closeOnDrawer);
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
          "image-src": "graph_solver.png",
          title: `${__props.nodeId}: Graph Solver`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Graph Solver",
            intro: "Find groups in your data"
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
