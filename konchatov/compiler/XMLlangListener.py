# Generated from XMLlang.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .XMLlangParser import XMLlangParser
else:
    from XMLlangParser import XMLlangParser

# This class defines a complete listener for a parse tree produced by XMLlangParser.
class XMLlangListener(ParseTreeListener):

    # Enter a parse tree produced by XMLlangParser#start.
    def enterStart(self, ctx:XMLlangParser.StartContext):
        pass

    # Exit a parse tree produced by XMLlangParser#start.
    def exitStart(self, ctx:XMLlangParser.StartContext):
        pass


    # Enter a parse tree produced by XMLlangParser#program.
    def enterProgram(self, ctx:XMLlangParser.ProgramContext):
        pass

    # Exit a parse tree produced by XMLlangParser#program.
    def exitProgram(self, ctx:XMLlangParser.ProgramContext):
        pass


    # Enter a parse tree produced by XMLlangParser#def.
    def enterDef(self, ctx:XMLlangParser.DefContext):
        pass

    # Exit a parse tree produced by XMLlangParser#def.
    def exitDef(self, ctx:XMLlangParser.DefContext):
        pass


    # Enter a parse tree produced by XMLlangParser#defDecl.
    def enterDefDecl(self, ctx:XMLlangParser.DefDeclContext):
        pass

    # Exit a parse tree produced by XMLlangParser#defDecl.
    def exitDefDecl(self, ctx:XMLlangParser.DefDeclContext):
        pass


    # Enter a parse tree produced by XMLlangParser#stat.
    def enterStat(self, ctx:XMLlangParser.StatContext):
        pass

    # Exit a parse tree produced by XMLlangParser#stat.
    def exitStat(self, ctx:XMLlangParser.StatContext):
        pass


    # Enter a parse tree produced by XMLlangParser#conCycOperator.
    def enterConCycOperator(self, ctx:XMLlangParser.ConCycOperatorContext):
        pass

    # Exit a parse tree produced by XMLlangParser#conCycOperator.
    def exitConCycOperator(self, ctx:XMLlangParser.ConCycOperatorContext):
        pass


    # Enter a parse tree produced by XMLlangParser#ifcon.
    def enterIfcon(self, ctx:XMLlangParser.IfconContext):
        pass

    # Exit a parse tree produced by XMLlangParser#ifcon.
    def exitIfcon(self, ctx:XMLlangParser.IfconContext):
        pass


    # Enter a parse tree produced by XMLlangParser#switchcon.
    def enterSwitchcon(self, ctx:XMLlangParser.SwitchconContext):
        pass

    # Exit a parse tree produced by XMLlangParser#switchcon.
    def exitSwitchcon(self, ctx:XMLlangParser.SwitchconContext):
        pass


    # Enter a parse tree produced by XMLlangParser#forcon.
    def enterForcon(self, ctx:XMLlangParser.ForconContext):
        pass

    # Exit a parse tree produced by XMLlangParser#forcon.
    def exitForcon(self, ctx:XMLlangParser.ForconContext):
        pass


    # Enter a parse tree produced by XMLlangParser#whilecon.
    def enterWhilecon(self, ctx:XMLlangParser.WhileconContext):
        pass

    # Exit a parse tree produced by XMLlangParser#whilecon.
    def exitWhilecon(self, ctx:XMLlangParser.WhileconContext):
        pass


    # Enter a parse tree produced by XMLlangParser#body.
    def enterBody(self, ctx:XMLlangParser.BodyContext):
        pass

    # Exit a parse tree produced by XMLlangParser#body.
    def exitBody(self, ctx:XMLlangParser.BodyContext):
        pass


    # Enter a parse tree produced by XMLlangParser#assignment.
    def enterAssignment(self, ctx:XMLlangParser.AssignmentContext):
        pass

    # Exit a parse tree produced by XMLlangParser#assignment.
    def exitAssignment(self, ctx:XMLlangParser.AssignmentContext):
        pass


    # Enter a parse tree produced by XMLlangParser#typeList.
    def enterTypeList(self, ctx:XMLlangParser.TypeListContext):
        pass

    # Exit a parse tree produced by XMLlangParser#typeList.
    def exitTypeList(self, ctx:XMLlangParser.TypeListContext):
        pass


    # Enter a parse tree produced by XMLlangParser#opList.
    def enterOpList(self, ctx:XMLlangParser.OpListContext):
        pass

    # Exit a parse tree produced by XMLlangParser#opList.
    def exitOpList(self, ctx:XMLlangParser.OpListContext):
        pass


    # Enter a parse tree produced by XMLlangParser#assFunc.
    def enterAssFunc(self, ctx:XMLlangParser.AssFuncContext):
        pass

    # Exit a parse tree produced by XMLlangParser#assFunc.
    def exitAssFunc(self, ctx:XMLlangParser.AssFuncContext):
        pass


    # Enter a parse tree produced by XMLlangParser#statFunc.
    def enterStatFunc(self, ctx:XMLlangParser.StatFuncContext):
        pass

    # Exit a parse tree produced by XMLlangParser#statFunc.
    def exitStatFunc(self, ctx:XMLlangParser.StatFuncContext):
        pass


    # Enter a parse tree produced by XMLlangParser#read.
    def enterRead(self, ctx:XMLlangParser.ReadContext):
        pass

    # Exit a parse tree produced by XMLlangParser#read.
    def exitRead(self, ctx:XMLlangParser.ReadContext):
        pass


    # Enter a parse tree produced by XMLlangParser#write.
    def enterWrite(self, ctx:XMLlangParser.WriteContext):
        pass

    # Exit a parse tree produced by XMLlangParser#write.
    def exitWrite(self, ctx:XMLlangParser.WriteContext):
        pass


    # Enter a parse tree produced by XMLlangParser#create.
    def enterCreate(self, ctx:XMLlangParser.CreateContext):
        pass

    # Exit a parse tree produced by XMLlangParser#create.
    def exitCreate(self, ctx:XMLlangParser.CreateContext):
        pass


    # Enter a parse tree produced by XMLlangParser#createDoc.
    def enterCreateDoc(self, ctx:XMLlangParser.CreateDocContext):
        pass

    # Exit a parse tree produced by XMLlangParser#createDoc.
    def exitCreateDoc(self, ctx:XMLlangParser.CreateDocContext):
        pass


    # Enter a parse tree produced by XMLlangParser#createNode.
    def enterCreateNode(self, ctx:XMLlangParser.CreateNodeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#createNode.
    def exitCreateNode(self, ctx:XMLlangParser.CreateNodeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#createAttribute.
    def enterCreateAttribute(self, ctx:XMLlangParser.CreateAttributeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#createAttribute.
    def exitCreateAttribute(self, ctx:XMLlangParser.CreateAttributeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#edit.
    def enterEdit(self, ctx:XMLlangParser.EditContext):
        pass

    # Exit a parse tree produced by XMLlangParser#edit.
    def exitEdit(self, ctx:XMLlangParser.EditContext):
        pass


    # Enter a parse tree produced by XMLlangParser#docEdit.
    def enterDocEdit(self, ctx:XMLlangParser.DocEditContext):
        pass

    # Exit a parse tree produced by XMLlangParser#docEdit.
    def exitDocEdit(self, ctx:XMLlangParser.DocEditContext):
        pass


    # Enter a parse tree produced by XMLlangParser#nodeEdite.
    def enterNodeEdite(self, ctx:XMLlangParser.NodeEditeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#nodeEdite.
    def exitNodeEdite(self, ctx:XMLlangParser.NodeEditeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#attributeEdit.
    def enterAttributeEdit(self, ctx:XMLlangParser.AttributeEditContext):
        pass

    # Exit a parse tree produced by XMLlangParser#attributeEdit.
    def exitAttributeEdit(self, ctx:XMLlangParser.AttributeEditContext):
        pass


    # Enter a parse tree produced by XMLlangParser#load.
    def enterLoad(self, ctx:XMLlangParser.LoadContext):
        pass

    # Exit a parse tree produced by XMLlangParser#load.
    def exitLoad(self, ctx:XMLlangParser.LoadContext):
        pass


    # Enter a parse tree produced by XMLlangParser#transform.
    def enterTransform(self, ctx:XMLlangParser.TransformContext):
        pass

    # Exit a parse tree produced by XMLlangParser#transform.
    def exitTransform(self, ctx:XMLlangParser.TransformContext):
        pass


    # Enter a parse tree produced by XMLlangParser#xmldelete.
    def enterXmldelete(self, ctx:XMLlangParser.XmldeleteContext):
        pass

    # Exit a parse tree produced by XMLlangParser#xmldelete.
    def exitXmldelete(self, ctx:XMLlangParser.XmldeleteContext):
        pass


    # Enter a parse tree produced by XMLlangParser#save.
    def enterSave(self, ctx:XMLlangParser.SaveContext):
        pass

    # Exit a parse tree produced by XMLlangParser#save.
    def exitSave(self, ctx:XMLlangParser.SaveContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getAttribute.
    def enterGetAttribute(self, ctx:XMLlangParser.GetAttributeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getAttribute.
    def exitGetAttribute(self, ctx:XMLlangParser.GetAttributeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#addAttribute.
    def enterAddAttribute(self, ctx:XMLlangParser.AddAttributeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#addAttribute.
    def exitAddAttribute(self, ctx:XMLlangParser.AddAttributeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#append.
    def enterAppend(self, ctx:XMLlangParser.AppendContext):
        pass

    # Exit a parse tree produced by XMLlangParser#append.
    def exitAppend(self, ctx:XMLlangParser.AppendContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getNodeText.
    def enterGetNodeText(self, ctx:XMLlangParser.GetNodeTextContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getNodeText.
    def exitGetNodeText(self, ctx:XMLlangParser.GetNodeTextContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getName.
    def enterGetName(self, ctx:XMLlangParser.GetNameContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getName.
    def exitGetName(self, ctx:XMLlangParser.GetNameContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getValue.
    def enterGetValue(self, ctx:XMLlangParser.GetValueContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getValue.
    def exitGetValue(self, ctx:XMLlangParser.GetValueContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getNodes.
    def enterGetNodes(self, ctx:XMLlangParser.GetNodesContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getNodes.
    def exitGetNodes(self, ctx:XMLlangParser.GetNodesContext):
        pass


    # Enter a parse tree produced by XMLlangParser#getListElement.
    def enterGetListElement(self, ctx:XMLlangParser.GetListElementContext):
        pass

    # Exit a parse tree produced by XMLlangParser#getListElement.
    def exitGetListElement(self, ctx:XMLlangParser.GetListElementContext):
        pass


    # Enter a parse tree produced by XMLlangParser#nodeSumm.
    def enterNodeSumm(self, ctx:XMLlangParser.NodeSummContext):
        pass

    # Exit a parse tree produced by XMLlangParser#nodeSumm.
    def exitNodeSumm(self, ctx:XMLlangParser.NodeSummContext):
        pass


    # Enter a parse tree produced by XMLlangParser#condition.
    def enterCondition(self, ctx:XMLlangParser.ConditionContext):
        pass

    # Exit a parse tree produced by XMLlangParser#condition.
    def exitCondition(self, ctx:XMLlangParser.ConditionContext):
        pass


    # Enter a parse tree produced by XMLlangParser#returnVal.
    def enterReturnVal(self, ctx:XMLlangParser.ReturnValContext):
        pass

    # Exit a parse tree produced by XMLlangParser#returnVal.
    def exitReturnVal(self, ctx:XMLlangParser.ReturnValContext):
        pass


    # Enter a parse tree produced by XMLlangParser#defCall.
    def enterDefCall(self, ctx:XMLlangParser.DefCallContext):
        pass

    # Exit a parse tree produced by XMLlangParser#defCall.
    def exitDefCall(self, ctx:XMLlangParser.DefCallContext):
        pass


    # Enter a parse tree produced by XMLlangParser#type.
    def enterType(self, ctx:XMLlangParser.TypeContext):
        pass

    # Exit a parse tree produced by XMLlangParser#type.
    def exitType(self, ctx:XMLlangParser.TypeContext):
        pass


    # Enter a parse tree produced by XMLlangParser#list.
    def enterList(self, ctx:XMLlangParser.ListContext):
        pass

    # Exit a parse tree produced by XMLlangParser#list.
    def exitList(self, ctx:XMLlangParser.ListContext):
        pass


    # Enter a parse tree produced by XMLlangParser#val.
    def enterVal(self, ctx:XMLlangParser.ValContext):
        pass

    # Exit a parse tree produced by XMLlangParser#val.
    def exitVal(self, ctx:XMLlangParser.ValContext):
        pass



del XMLlangParser