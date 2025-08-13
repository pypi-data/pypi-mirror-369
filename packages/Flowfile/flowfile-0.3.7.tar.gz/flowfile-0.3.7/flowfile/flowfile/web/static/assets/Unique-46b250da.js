import { r as ref, d as defineComponent, l as computed, n as onMounted, R as nextTick, o as onUnmounted, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, h as createBlock, u as unref, _ as _export_sfc, a7 as Teleport, i as createCommentVNode } from "./index-f6c15e76.js";
import { C as CodeLoader } from "./vue-content-loader.es-0371da73.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { s as selectDynamic } from "./selectDynamic-af36165e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./UnavailableFields-a1768e52.js";
import "./designer-13eabd83.js";
const createSelectInputFromName = (columnName, keep = true) => {
  return {
    old_name: columnName,
    new_name: columnName,
    keep,
    is_altered: false,
    data_type_change: false,
    is_available: true,
    position: 0,
    original_position: 0
  };
};
ref(null);
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "unique",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const showContextMenu = ref(false);
    const showContextMenuRemove = ref(false);
    const dataLoaded = ref(false);
    const contextMenuColumn = ref(null);
    const contextMenuRef = ref(null);
    const nodeUnique = ref(null);
    const nodeData = ref(null);
    const selection = ref([]);
    const uniqueInput2 = ref({
      columns: [],
      strategy: "any"
    });
    const loadSelection = (nodeData2, columnsToKeep) => {
      var _a;
      if ((_a = nodeData2.main_input) == null ? void 0 : _a.columns) {
        selection.value = nodeData2.main_input.columns.map((column) => {
          const keep = columnsToKeep.includes(column);
          return createSelectInputFromName(column, keep);
        });
      }
    };
    const loadData = async (nodeId) => {
      var _a;
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodeUnique.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      dataLoaded.value = true;
      if (nodeData.value) {
        if (nodeUnique.value) {
          if (nodeUnique.value.unique_input) {
            uniqueInput2.value = nodeUnique.value.unique_input;
          } else {
            nodeUnique.value.unique_input = uniqueInput2.value;
          }
          loadSelection(nodeData.value, uniqueInput2.value.columns);
        }
      }
    };
    const calculateSelects = (updatedInputs) => {
      console.log(updatedInputs);
      selection.value = updatedInputs;
      uniqueInput2.value.columns = updatedInputs.filter((input) => input.keep).map((input) => input.old_name);
    };
    const setUniqueColumns = () => {
      uniqueInput2.value.columns = selection.value.filter((input) => input.keep).map((input) => input.old_name);
    };
    const loadNodeData = async (nodeId) => {
      loadData(nodeId);
      dataLoaded.value = true;
      nodeStore.isDrawerOpen = true;
    };
    const handleClickOutside = (event) => {
      var _a;
      if (!((_a = contextMenuRef.value) == null ? void 0 : _a.contains(event.target))) {
        showContextMenu.value = false;
        contextMenuColumn.value = null;
        showContextMenuRemove.value = false;
      }
    };
    const getMissingColumns = (availableColumns, usedColumns) => {
      const availableSet = new Set(availableColumns);
      return Array.from(new Set(usedColumns.filter((usedColumn) => !availableSet.has(usedColumn))));
    };
    const missingColumns = computed(() => {
      var _a, _b;
      if (nodeData.value && ((_a = nodeData.value.main_input) == null ? void 0 : _a.columns)) {
        return getMissingColumns((_b = nodeData.value.main_input) == null ? void 0 : _b.columns, uniqueInput2.value.columns);
      }
      return [];
    });
    const calculateMissingColumns = () => {
      var _a, _b;
      if (nodeData.value && ((_a = nodeData.value.main_input) == null ? void 0 : _a.columns)) {
        return getMissingColumns((_b = nodeData.value.main_input) == null ? void 0 : _b.columns, uniqueInput2.value.columns);
      }
      return [];
    };
    const validateNode = async () => {
      var _a, _b;
      if ((_a = nodeUnique.value) == null ? void 0 : _a.unique_input) {
        await loadData(Number(nodeUnique.value.node_id));
      }
      const missingColumnsLocal = calculateMissingColumns();
      if (missingColumnsLocal.length > 0 && nodeUnique.value) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: false,
          error: `The fields ${missingColumns.value.join(", ")} are missing in the available columns.`
        });
      } else if (((_b = nodeUnique.value) == null ? void 0 : _b.unique_input.columns.length) == 0) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: false,
          error: "Please select at least one field."
        });
      } else if (nodeUnique.value) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: true,
          error: ""
        });
      }
    };
    const instantValidate = async () => {
      var _a;
      if (missingColumns.value.length > 0 && nodeUnique.value) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: false,
          error: `The fields ${missingColumns.value.join(", ")} are missing in the available columns.`
        });
      } else if (((_a = nodeUnique.value) == null ? void 0 : _a.unique_input.columns.length) == 0) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: false,
          error: "Please select at least one field."
        });
      } else if (nodeUnique.value) {
        nodeStore.setNodeValidation(nodeUnique.value.node_id, {
          isValid: true,
          error: ""
        });
      }
    };
    const pushNodeData = async () => {
      var _a, _b, _c, _d;
      dataLoaded.value = false;
      setUniqueColumns();
      nodeStore.isDrawerOpen = false;
      console.log("doing this");
      console.log((_a = nodeUnique.value) == null ? void 0 : _a.is_setup);
      console.log(nodeUnique.value);
      if ((_b = nodeUnique.value) == null ? void 0 : _b.is_setup) {
        nodeUnique.value.is_setup = true;
      }
      nodeStore.updateSettings(nodeUnique);
      await instantValidate();
      if ((_c = nodeUnique.value) == null ? void 0 : _c.unique_input) {
        nodeStore.setNodeValidateFunc((_d = nodeUnique.value) == null ? void 0 : _d.node_id, validateNode);
      }
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
      return dataLoaded.value && nodeUnique.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeUnique.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => nodeUnique.value = $event)
        }, {
          default: withCtx(() => [
            createVNode(selectDynamic, {
              "select-inputs": selection.value,
              "show-keep-option": true,
              "show-data-type": false,
              "show-new-columns": false,
              "show-old-columns": true,
              "show-headers": true,
              "show-title": false,
              "show-data": true,
              title: "Select data",
              "original-column-header": "Column",
              onUpdateSelectInputs: calculateSelects
            }, null, 8, ["select-inputs"])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const unique_vue_vue_type_style_index_0_scoped_8edf8bb6_lang = "";
const uniqueInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-8edf8bb6"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Unique",
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
          "image-src": "unique.png",
          title: `${__props.nodeId}: Drop duplicates`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Drop duplicates",
            intro: "Make the table unique by one or more columns"
          }),
          createVNode(uniqueInput, {
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
