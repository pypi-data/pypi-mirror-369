import { C as CodeLoader } from "./vue-content-loader.es-0371da73.js";
import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { s as selectDynamic } from "./selectDynamic-af36165e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { d as defineComponent, r as ref, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, h as createBlock, u as unref, _ as _export_sfc, n as onMounted, R as nextTick, a7 as Teleport, i as createCommentVNode } from "./index-f6c15e76.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./UnavailableFields-a1768e52.js";
import "./designer-13eabd83.js";
const _hoisted_1$1 = { key: 0 };
const _hoisted_2 = { class: "listbox-wrapper" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "crossJoin",
  setup(__props, { expose: __expose }) {
    const result = ref(null);
    const nodeStore = useNodeStore();
    const dataLoaded = ref(false);
    const nodeCrossJoin = ref(null);
    const updateSelectInputsHandler = (updatedInputs, isLeft) => {
      if (isLeft && nodeCrossJoin.value) {
        nodeCrossJoin.value.cross_join_input.left_select.renames = updatedInputs;
      } else if (nodeCrossJoin.value) {
        nodeCrossJoin.value.cross_join_input.right_select.renames = updatedInputs;
      }
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      result.value = await nodeStore.getNodeData(nodeId, false);
      nodeCrossJoin.value = (_a = result.value) == null ? void 0 : _a.setting_input;
      console.log(result.value);
      if (result.value) {
        console.log("Data loaded");
        dataLoaded.value = true;
      }
      nodeStore.isDrawerOpen = true;
    };
    const pushNodeData = async () => {
      console.log("Pushing node data");
      nodeStore.updateSettings(nodeCrossJoin);
      nodeStore.isDrawerOpen = false;
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      return dataLoaded.value && nodeCrossJoin.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeCrossJoin.value,
          "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => nodeCrossJoin.value = $event)
        }, {
          default: withCtx(() => {
            var _a, _b;
            return [
              createBaseVNode("div", _hoisted_2, [
                createVNode(selectDynamic, {
                  "select-inputs": (_a = nodeCrossJoin.value) == null ? void 0 : _a.cross_join_input.left_select.renames,
                  "show-keep-option": true,
                  "show-title": true,
                  "show-headers": true,
                  "show-data": true,
                  title: "Left data",
                  onUpdateSelectInputs: _cache[0] || (_cache[0] = (updatedInputs) => updateSelectInputsHandler(updatedInputs, true))
                }, null, 8, ["select-inputs"]),
                createVNode(selectDynamic, {
                  "select-inputs": (_b = nodeCrossJoin.value) == null ? void 0 : _b.cross_join_input.right_select.renames,
                  "show-keep-option": true,
                  "show-headers": true,
                  "show-title": true,
                  "show-data": true,
                  title: "Right data",
                  onUpdateSelectInputs: _cache[1] || (_cache[1] = (updatedInputs) => updateSelectInputsHandler(updatedInputs, true))
                }, null, 8, ["select-inputs"])
              ])
            ];
          }),
          _: 1
        }, 8, ["modelValue"])
      ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 1 }));
    };
  }
});
const crossJoin_vue_vue_type_style_index_0_scoped_de068ad8_lang = "";
const joinInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-de068ad8"]]);
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "CrossJoin",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const childComp = ref(null);
    const drawer = ref(false);
    const props = __props;
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
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(NodeButton, {
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "cross_join.png",
          title: `${__props.nodeId}: Join`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Join",
            intro: "Combine datasets based on one or more columns."
          }),
          createVNode(joinInput, {
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
