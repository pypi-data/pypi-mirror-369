import { u as useNodeStore } from "./vue-codemirror.esm-2847001e.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-71e11604.js";
import { d as defineComponent, r as ref, n as onMounted, R as nextTick, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, i as createCommentVNode, h as createBlock, a7 as Teleport } from "./index-f6c15e76.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-988d9efe.js";
import "./designer-13eabd83.js";
const _hoisted_1$1 = {
  key: 0,
  class: "listbox-wrapper"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "RecordCount",
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const dataLoaded = ref(false);
    const nodeData = ref(null);
    const nodeRecordCount = ref(null);
    const loadNodeData = async (nodeId) => {
      var _a;
      nodeData.value = await nodeStore.getNodeData(nodeId, false);
      nodeRecordCount.value = (_a = nodeData.value) == null ? void 0 : _a.setting_input;
      dataLoaded.value = true;
      nodeStore.isDrawerOpen = true;
    };
    const pushNodeData = async () => {
      if (nodeRecordCount.value) {
        nodeStore.updateSettings(nodeRecordCount);
      }
      nodeStore.isDrawerOpen = false;
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return dataLoaded.value && nodeRecordCount.value ? (openBlock(), createElementBlock("div", _hoisted_1$1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeRecordCount.value,
          "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => nodeRecordCount.value = $event)
        }, {
          default: withCtx(() => _cache[1] || (_cache[1] = [
            createBaseVNode("p", null, " This node helps you quickly retrieve the total number of records from the selected table. It's a simple yet powerful tool to keep track of the data volume as you work through your tasks. ", -1),
            createBaseVNode("p", null, "This node does not need a setup", -1)
          ])),
          _: 1,
          __: [1]
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const _hoisted_1 = { ref: "el" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "RecordCount",
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
          "image-src": "record_count.png",
          title: `${__props.nodeId}: Count records`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Count records",
            intro: "Get the count of the number of reocrds"
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
