import { d as defineComponent, r as ref, b as resolveComponent, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, g as createTextVNode, i as createCommentVNode, u as unref, a5 as withDirectives, a6 as vModelText, h as createBlock, _ as _export_sfc, n as onMounted, R as nextTick, a7 as Teleport } from "./index-f6c15e76.js";
import { C as CodeLoader } from "./vue-content-loader.es-0371da73.js";
import { C as ColumnSelector } from "./dropDown-13564764.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import mainEditorRef from "./fullEditor-fd2cd6f9.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1 = { key: 0 };
const _hoisted_2 = { class: "listbox-wrapper" };
const _hoisted_3 = { style: { "border-radius": "20px" } };
const _hoisted_4 = { key: 0 };
const _hoisted_5 = { key: 1 };
const _hoisted_6 = { class: "selectors-row" };
const _hoisted_7 = { key: 0 };
const _hoisted_8 = { key: 1 };
const _hoisted_9 = { key: 2 };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "filter",
  setup(__props, { expose: __expose }) {
    const editorString = ref("");
    const isLoaded = ref(false);
    const isAdvancedFilter = ref(true);
    const nodeStore = useNodeStore();
    const nodeFilter = ref(null);
    const nodeData = ref(null);
    const showOptions = ref(false);
    const editorChild = ref(null);
    const comparisonMapping = {
      Equals: "=",
      "Smaller then": "<",
      "Greater then": ">",
      Contains: "contains",
      // or any other representation you prefer
      "Does not equal": "!=",
      "Smaller or equal": "<=",
      "Greater or equal": ">="
    };
    const reversedMapping = {};
    Object.entries(comparisonMapping).forEach(([key, value]) => {
      reversedMapping[value] = key;
    });
    const translateSymbolToDes = (symbol) => {
      return reversedMapping[symbol] ?? symbol;
    };
    const comparisonOptions = Object.keys(comparisonMapping);
    const handleFieldChange = (newValue) => {
      var _a;
      if ((_a = nodeFilter.value) == null ? void 0 : _a.filter_input.basic_filter) {
        nodeFilter.value.filter_input.basic_filter.field = newValue;
      }
    };
    function translateComparison(input) {
      return comparisonMapping[input] ?? input;
    }
    const handleFilterTypeChange = (newValue) => {
      var _a;
      if ((_a = nodeFilter.value) == null ? void 0 : _a.filter_input.basic_filter) {
        const symbolicType = translateComparison(newValue);
        nodeFilter.value.filter_input.basic_filter.filter_type = symbolicType;
      }
    };
    const loadNodeData = async (nodeId) => {
      var _a, _b, _c;
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      if (nodeData.value) {
        nodeFilter.value = nodeData.value.setting_input;
        if ((_a = nodeFilter.value) == null ? void 0 : _a.filter_input.advanced_filter) {
          editorString.value = (_b = nodeFilter.value) == null ? void 0 : _b.filter_input.advanced_filter;
        }
        isAdvancedFilter.value = ((_c = nodeFilter.value) == null ? void 0 : _c.filter_input.filter_type) === "advanced";
      }
      isLoaded.value = true;
    };
    const updateAdvancedFilter = () => {
      if (nodeFilter.value) {
        nodeFilter.value.filter_input.advanced_filter = nodeStore.inputCode;
        console.log(nodeFilter.value);
      }
    };
    const pushNodeData = async () => {
      if (nodeFilter.value) {
        if (isAdvancedFilter.value) {
          updateAdvancedFilter();
          nodeFilter.value.filter_input.filter_type = "advanced";
        } else {
          nodeFilter.value.filter_input.filter_type = "basic";
        }
        nodeStore.updateSettings(nodeFilter);
      }
      isLoaded.value = false;
      nodeStore.isDrawerOpen = false;
    };
    __expose({ loadNodeData, pushNodeData });
    return (_ctx, _cache) => {
      const _component_el_switch = resolveComponent("el-switch");
      return isLoaded.value && nodeFilter.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeFilter.value,
          "onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => nodeFilter.value = $event)
        }, {
          default: withCtx(() => {
            var _a, _b, _c, _d, _e;
            return [
              createBaseVNode("div", _hoisted_2, [
                createBaseVNode("div", _hoisted_3, [
                  createVNode(_component_el_switch, {
                    modelValue: isAdvancedFilter.value,
                    "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => isAdvancedFilter.value = $event),
                    class: "mb-2",
                    "active-text": "Advanced filter options",
                    "inactive-text": "Basic filter"
                  }, null, 8, ["modelValue"])
                ]),
                isAdvancedFilter.value ? (openBlock(), createElementBlock("div", _hoisted_4, [
                  _cache[7] || (_cache[7] = createTextVNode(" Advanced filter ")),
                  createVNode(mainEditorRef, {
                    ref_key: "editorChild",
                    ref: editorChild,
                    "editor-string": editorString.value
                  }, null, 8, ["editor-string"])
                ])) : createCommentVNode("", true),
                !isAdvancedFilter.value ? (openBlock(), createElementBlock("div", _hoisted_5, [
                  _cache[8] || (_cache[8] = createTextVNode(" Standard Filter ")),
                  createBaseVNode("div", _hoisted_6, [
                    ((_a = nodeFilter.value) == null ? void 0 : _a.filter_input.basic_filter) ? (openBlock(), createElementBlock("div", _hoisted_7, [
                      createVNode(ColumnSelector, {
                        modelValue: nodeFilter.value.filter_input.basic_filter.field,
                        "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeFilter.value.filter_input.basic_filter.field = $event),
                        value: nodeFilter.value.filter_input.basic_filter.field,
                        "column-options": (_c = (_b = nodeData.value) == null ? void 0 : _b.main_input) == null ? void 0 : _c.columns,
                        "onUpdate:value": _cache[2] || (_cache[2] = (value) => handleFieldChange(value))
                      }, null, 8, ["modelValue", "value", "column-options"])
                    ])) : createCommentVNode("", true),
                    ((_d = nodeFilter.value) == null ? void 0 : _d.filter_input.basic_filter) ? (openBlock(), createElementBlock("div", _hoisted_8, [
                      createVNode(ColumnSelector, {
                        value: translateSymbolToDes(nodeFilter.value.filter_input.basic_filter.filter_type),
                        "column-options": unref(comparisonOptions),
                        "onUpdate:value": _cache[3] || (_cache[3] = (value) => handleFilterTypeChange(value))
                      }, null, 8, ["value", "column-options"])
                    ])) : createCommentVNode("", true),
                    ((_e = nodeFilter.value) == null ? void 0 : _e.filter_input.basic_filter) ? (openBlock(), createElementBlock("div", _hoisted_9, [
                      withDirectives(createBaseVNode("input", {
                        "onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => nodeFilter.value.filter_input.basic_filter.filter_value = $event),
                        type: "text",
                        class: "input-field",
                        onFocus: _cache[5] || (_cache[5] = ($event) => showOptions.value = true)
                      }, null, 544), [
                        [vModelText, nodeFilter.value.filter_input.basic_filter.filter_value]
                      ])
                    ])) : createCommentVNode("", true)
                  ])
                ])) : createCommentVNode("", true)
              ])
            ];
          }),
          _: 1
        }, 8, ["modelValue"])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const filter_vue_vue_type_style_index_0_scoped_84dc735d_lang = "";
const filterInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-84dc735d"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "Filter",
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
          "image-src": "filter.png",
          title: `${__props.nodeId}: Filter`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Filter data",
            intro: "Filter rows in the data"
          }),
          createVNode(filterInput, {
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
