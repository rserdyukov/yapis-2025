// Generated from d:/Study/Univer/4_kurs/YAPIS/Rep/yapis-2025/verkovich/grammar/mcl_parcer.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue"})
public class mcl_parcer extends Parser {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		IF=1, ELSE=2, WHILE=3, UNTIL=4, FOR=5, IN=6, FUNC=7, RETURN=8, VOID_TYPE=9, 
		LAMBDA=10, AND=11, OR=12, NOT=13, TRUE=14, FALSE=15, INT_TYPE=16, FLOAT_TYPE=17, 
		VECTOR_TYPE=18, MATRIX_TYPE=19, TUPLE_TYPE=20, BOOLEAN_TYPE=21, STRING_TYPE=22, 
		NAN=23, INFINITY=24, FLOAT=25, INTEGER=26, STRING=27, PLUS=28, MINUS=29, 
		MUL=30, DIV=31, POW=32, MOD=33, EQ=34, NEQ=35, GT=36, LT=37, GTE=38, LTE=39, 
		ASSIGN=40, LPAREN=41, RPAREN=42, LBRACE=43, RBRACE=44, LBRACK=45, RBRACK=46, 
		VBAR=47, COMMA=48, COLON=49, ARROW=50, QMARK=51, IDENTIFIER=52, COMMENT=53, 
		WS=54, NL=55, INDENT=56, DEDENT=57;
	public static final int
		RULE_program = 0, RULE_suite = 1, RULE_functionDefinition = 2, RULE_parameterList = 3, 
		RULE_parameter = 4, RULE_type = 5, RULE_scalarType = 6, RULE_vectorType = 7, 
		RULE_statement = 8, RULE_assignment = 9, RULE_functionCall = 10, RULE_argumentList = 11, 
		RULE_ifStatement = 12, RULE_whileStatement = 13, RULE_untilStatement = 14, 
		RULE_forStatement = 15, RULE_returnStatement = 16, RULE_expression = 17, 
		RULE_logicalOrExpression = 18, RULE_logicalAndExpression = 19, RULE_equalityExpression = 20, 
		RULE_relationalExpression = 21, RULE_additiveExpression = 22, RULE_multiplicativeExpression = 23, 
		RULE_unaryExpression = 24, RULE_powerExpression = 25, RULE_primary = 26, 
		RULE_literal = 27, RULE_vectorLiteral = 28, RULE_matrixLiteral = 29, RULE_expressionList = 30, 
		RULE_creator = 31, RULE_lambdaExpression = 32;
	private static String[] makeRuleNames() {
		return new String[] {
			"program", "suite", "functionDefinition", "parameterList", "parameter", 
			"type", "scalarType", "vectorType", "statement", "assignment", "functionCall", 
			"argumentList", "ifStatement", "whileStatement", "untilStatement", "forStatement", 
			"returnStatement", "expression", "logicalOrExpression", "logicalAndExpression", 
			"equalityExpression", "relationalExpression", "additiveExpression", "multiplicativeExpression", 
			"unaryExpression", "powerExpression", "primary", "literal", "vectorLiteral", 
			"matrixLiteral", "expressionList", "creator", "lambdaExpression"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'if'", "'else'", "'while'", "'until'", "'for'", "'in'", "'func'", 
			"'return'", "'void'", "'lambda'", "'and'", "'or'", "'not'", "'true'", 
			"'false'", "'int'", "'float'", "'vector'", "'matrix'", "'tuple'", "'boolean'", 
			"'string'", "'NaN'", "'Infinity'", null, null, null, "'+'", "'-'", "'*'", 
			"'/'", "'^'", "'%'", "'=='", "'!='", "'>'", "'<'", "'>='", "'<='", "'='", 
			"'('", "')'", "'{'", "'}'", "'['", "']'", "'|'", "','", "':'", "'->'", 
			"'?'", null, null, null, null, "'indent'", "'dedent'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "IF", "ELSE", "WHILE", "UNTIL", "FOR", "IN", "FUNC", "RETURN", 
			"VOID_TYPE", "LAMBDA", "AND", "OR", "NOT", "TRUE", "FALSE", "INT_TYPE", 
			"FLOAT_TYPE", "VECTOR_TYPE", "MATRIX_TYPE", "TUPLE_TYPE", "BOOLEAN_TYPE", 
			"STRING_TYPE", "NAN", "INFINITY", "FLOAT", "INTEGER", "STRING", "PLUS", 
			"MINUS", "MUL", "DIV", "POW", "MOD", "EQ", "NEQ", "GT", "LT", "GTE", 
			"LTE", "ASSIGN", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACK", "RBRACK", 
			"VBAR", "COMMA", "COLON", "ARROW", "QMARK", "IDENTIFIER", "COMMENT", 
			"WS", "NL", "INDENT", "DEDENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "mcl_parcer.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public mcl_parcer(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ProgramContext extends ParserRuleContext {
		public TerminalNode EOF() { return getToken(mcl_parcer.EOF, 0); }
		public List<FunctionDefinitionContext> functionDefinition() {
			return getRuleContexts(FunctionDefinitionContext.class);
		}
		public FunctionDefinitionContext functionDefinition(int i) {
			return getRuleContext(FunctionDefinitionContext.class,i);
		}
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ProgramContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_program; }
	}

	public final ProgramContext program() throws RecognitionException {
		ProgramContext _localctx = new ProgramContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_program);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(69);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==FUNC) {
				{
				{
				setState(66);
				functionDefinition();
				}
				}
				setState(71);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(75);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & 4503599635694394L) != 0)) {
				{
				{
				setState(72);
				statement();
				}
				}
				setState(77);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(78);
			match(EOF);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class SuiteContext extends ParserRuleContext {
		public TerminalNode NL() { return getToken(mcl_parcer.NL, 0); }
		public TerminalNode INDENT() { return getToken(mcl_parcer.INDENT, 0); }
		public TerminalNode DEDENT() { return getToken(mcl_parcer.DEDENT, 0); }
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public SuiteContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_suite; }
	}

	public final SuiteContext suite() throws RecognitionException {
		SuiteContext _localctx = new SuiteContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_suite);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(80);
			match(NL);
			setState(81);
			match(INDENT);
			setState(83); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(82);
				statement();
				}
				}
				setState(85); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & 4503599635694394L) != 0) );
			setState(87);
			match(DEDENT);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class FunctionDefinitionContext extends ParserRuleContext {
		public TerminalNode FUNC() { return getToken(mcl_parcer.FUNC, 0); }
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public TerminalNode LPAREN() { return getToken(mcl_parcer.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(mcl_parcer.RPAREN, 0); }
		public TerminalNode ARROW() { return getToken(mcl_parcer.ARROW, 0); }
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public SuiteContext suite() {
			return getRuleContext(SuiteContext.class,0);
		}
		public ParameterListContext parameterList() {
			return getRuleContext(ParameterListContext.class,0);
		}
		public FunctionDefinitionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_functionDefinition; }
	}

	public final FunctionDefinitionContext functionDefinition() throws RecognitionException {
		FunctionDefinitionContext _localctx = new FunctionDefinitionContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_functionDefinition);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(89);
			match(FUNC);
			setState(90);
			match(IDENTIFIER);
			setState(91);
			match(LPAREN);
			setState(93);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==IDENTIFIER) {
				{
				setState(92);
				parameterList();
				}
			}

			setState(95);
			match(RPAREN);
			setState(96);
			match(ARROW);
			setState(97);
			type();
			setState(98);
			match(COLON);
			setState(99);
			suite();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ParameterListContext extends ParserRuleContext {
		public List<ParameterContext> parameter() {
			return getRuleContexts(ParameterContext.class);
		}
		public ParameterContext parameter(int i) {
			return getRuleContext(ParameterContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(mcl_parcer.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(mcl_parcer.COMMA, i);
		}
		public ParameterListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_parameterList; }
	}

	public final ParameterListContext parameterList() throws RecognitionException {
		ParameterListContext _localctx = new ParameterListContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_parameterList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(101);
			parameter();
			setState(106);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(102);
				match(COMMA);
				setState(103);
				parameter();
				}
				}
				setState(108);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ParameterContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public ParameterContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_parameter; }
	}

	public final ParameterContext parameter() throws RecognitionException {
		ParameterContext _localctx = new ParameterContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_parameter);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(109);
			match(IDENTIFIER);
			setState(110);
			match(COLON);
			setState(111);
			type();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class TypeContext extends ParserRuleContext {
		public ScalarTypeContext scalarType() {
			return getRuleContext(ScalarTypeContext.class,0);
		}
		public VectorTypeContext vectorType() {
			return getRuleContext(VectorTypeContext.class,0);
		}
		public TerminalNode MATRIX_TYPE() { return getToken(mcl_parcer.MATRIX_TYPE, 0); }
		public TerminalNode TUPLE_TYPE() { return getToken(mcl_parcer.TUPLE_TYPE, 0); }
		public TerminalNode BOOLEAN_TYPE() { return getToken(mcl_parcer.BOOLEAN_TYPE, 0); }
		public TerminalNode STRING_TYPE() { return getToken(mcl_parcer.STRING_TYPE, 0); }
		public TerminalNode VOID_TYPE() { return getToken(mcl_parcer.VOID_TYPE, 0); }
		public TypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_type; }
	}

	public final TypeContext type() throws RecognitionException {
		TypeContext _localctx = new TypeContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_type);
		try {
			setState(120);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INT_TYPE:
			case FLOAT_TYPE:
				enterOuterAlt(_localctx, 1);
				{
				setState(113);
				scalarType();
				}
				break;
			case VECTOR_TYPE:
				enterOuterAlt(_localctx, 2);
				{
				setState(114);
				vectorType();
				}
				break;
			case MATRIX_TYPE:
				enterOuterAlt(_localctx, 3);
				{
				setState(115);
				match(MATRIX_TYPE);
				}
				break;
			case TUPLE_TYPE:
				enterOuterAlt(_localctx, 4);
				{
				setState(116);
				match(TUPLE_TYPE);
				}
				break;
			case BOOLEAN_TYPE:
				enterOuterAlt(_localctx, 5);
				{
				setState(117);
				match(BOOLEAN_TYPE);
				}
				break;
			case STRING_TYPE:
				enterOuterAlt(_localctx, 6);
				{
				setState(118);
				match(STRING_TYPE);
				}
				break;
			case VOID_TYPE:
				enterOuterAlt(_localctx, 7);
				{
				setState(119);
				match(VOID_TYPE);
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ScalarTypeContext extends ParserRuleContext {
		public TerminalNode INT_TYPE() { return getToken(mcl_parcer.INT_TYPE, 0); }
		public TerminalNode FLOAT_TYPE() { return getToken(mcl_parcer.FLOAT_TYPE, 0); }
		public ScalarTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_scalarType; }
	}

	public final ScalarTypeContext scalarType() throws RecognitionException {
		ScalarTypeContext _localctx = new ScalarTypeContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_scalarType);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(122);
			_la = _input.LA(1);
			if ( !(_la==INT_TYPE || _la==FLOAT_TYPE) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class VectorTypeContext extends ParserRuleContext {
		public TerminalNode VECTOR_TYPE() { return getToken(mcl_parcer.VECTOR_TYPE, 0); }
		public VectorTypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_vectorType; }
	}

	public final VectorTypeContext vectorType() throws RecognitionException {
		VectorTypeContext _localctx = new VectorTypeContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_vectorType);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(124);
			match(VECTOR_TYPE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class StatementContext extends ParserRuleContext {
		public AssignmentContext assignment() {
			return getRuleContext(AssignmentContext.class,0);
		}
		public FunctionCallContext functionCall() {
			return getRuleContext(FunctionCallContext.class,0);
		}
		public IfStatementContext ifStatement() {
			return getRuleContext(IfStatementContext.class,0);
		}
		public WhileStatementContext whileStatement() {
			return getRuleContext(WhileStatementContext.class,0);
		}
		public UntilStatementContext untilStatement() {
			return getRuleContext(UntilStatementContext.class,0);
		}
		public ForStatementContext forStatement() {
			return getRuleContext(ForStatementContext.class,0);
		}
		public ReturnStatementContext returnStatement() {
			return getRuleContext(ReturnStatementContext.class,0);
		}
		public List<TerminalNode> NL() { return getTokens(mcl_parcer.NL); }
		public TerminalNode NL(int i) {
			return getToken(mcl_parcer.NL, i);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_statement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(133);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,6,_ctx) ) {
			case 1:
				{
				setState(126);
				assignment();
				}
				break;
			case 2:
				{
				setState(127);
				functionCall();
				}
				break;
			case 3:
				{
				setState(128);
				ifStatement();
				}
				break;
			case 4:
				{
				setState(129);
				whileStatement();
				}
				break;
			case 5:
				{
				setState(130);
				untilStatement();
				}
				break;
			case 6:
				{
				setState(131);
				forStatement();
				}
				break;
			case 7:
				{
				setState(132);
				returnStatement();
				}
				break;
			}
			setState(136); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(135);
				match(NL);
				}
				}
				setState(138); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==NL );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AssignmentContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public TerminalNode ASSIGN() { return getToken(mcl_parcer.ASSIGN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode QMARK() { return getToken(mcl_parcer.QMARK, 0); }
		public AssignmentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assignment; }
	}

	public final AssignmentContext assignment() throws RecognitionException {
		AssignmentContext _localctx = new AssignmentContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_assignment);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(143);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 8323584L) != 0)) {
				{
				setState(140);
				type();
				setState(141);
				match(QMARK);
				}
			}

			setState(145);
			match(IDENTIFIER);
			setState(146);
			match(ASSIGN);
			setState(147);
			expression(0);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class FunctionCallContext extends ParserRuleContext {
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public TerminalNode LPAREN() { return getToken(mcl_parcer.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(mcl_parcer.RPAREN, 0); }
		public ArgumentListContext argumentList() {
			return getRuleContext(ArgumentListContext.class,0);
		}
		public FunctionCallContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_functionCall; }
	}

	public final FunctionCallContext functionCall() throws RecognitionException {
		FunctionCallContext _localctx = new FunctionCallContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_functionCall);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(149);
			match(IDENTIFIER);
			setState(150);
			match(LPAREN);
			setState(152);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 4690517669502976L) != 0)) {
				{
				setState(151);
				argumentList();
				}
			}

			setState(154);
			match(RPAREN);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ArgumentListContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(mcl_parcer.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(mcl_parcer.COMMA, i);
		}
		public ArgumentListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argumentList; }
	}

	public final ArgumentListContext argumentList() throws RecognitionException {
		ArgumentListContext _localctx = new ArgumentListContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_argumentList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(156);
			expression(0);
			setState(161);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(157);
				match(COMMA);
				setState(158);
				expression(0);
				}
				}
				setState(163);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class IfStatementContext extends ParserRuleContext {
		public TerminalNode IF() { return getToken(mcl_parcer.IF, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public List<TerminalNode> COLON() { return getTokens(mcl_parcer.COLON); }
		public TerminalNode COLON(int i) {
			return getToken(mcl_parcer.COLON, i);
		}
		public List<SuiteContext> suite() {
			return getRuleContexts(SuiteContext.class);
		}
		public SuiteContext suite(int i) {
			return getRuleContext(SuiteContext.class,i);
		}
		public TerminalNode ELSE() { return getToken(mcl_parcer.ELSE, 0); }
		public IfStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ifStatement; }
	}

	public final IfStatementContext ifStatement() throws RecognitionException {
		IfStatementContext _localctx = new IfStatementContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_ifStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(164);
			match(IF);
			setState(165);
			expression(0);
			setState(166);
			match(COLON);
			setState(167);
			suite();
			setState(171);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ELSE) {
				{
				setState(168);
				match(ELSE);
				setState(169);
				match(COLON);
				setState(170);
				suite();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class WhileStatementContext extends ParserRuleContext {
		public TerminalNode WHILE() { return getToken(mcl_parcer.WHILE, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public SuiteContext suite() {
			return getRuleContext(SuiteContext.class,0);
		}
		public WhileStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_whileStatement; }
	}

	public final WhileStatementContext whileStatement() throws RecognitionException {
		WhileStatementContext _localctx = new WhileStatementContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_whileStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(173);
			match(WHILE);
			setState(174);
			expression(0);
			setState(175);
			match(COLON);
			setState(176);
			suite();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class UntilStatementContext extends ParserRuleContext {
		public TerminalNode UNTIL() { return getToken(mcl_parcer.UNTIL, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public SuiteContext suite() {
			return getRuleContext(SuiteContext.class,0);
		}
		public UntilStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_untilStatement; }
	}

	public final UntilStatementContext untilStatement() throws RecognitionException {
		UntilStatementContext _localctx = new UntilStatementContext(_ctx, getState());
		enterRule(_localctx, 28, RULE_untilStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(178);
			match(UNTIL);
			setState(179);
			expression(0);
			setState(180);
			match(COLON);
			setState(181);
			suite();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ForStatementContext extends ParserRuleContext {
		public TerminalNode FOR() { return getToken(mcl_parcer.FOR, 0); }
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public TerminalNode IN() { return getToken(mcl_parcer.IN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public SuiteContext suite() {
			return getRuleContext(SuiteContext.class,0);
		}
		public ForStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_forStatement; }
	}

	public final ForStatementContext forStatement() throws RecognitionException {
		ForStatementContext _localctx = new ForStatementContext(_ctx, getState());
		enterRule(_localctx, 30, RULE_forStatement);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(183);
			match(FOR);
			setState(184);
			match(IDENTIFIER);
			setState(185);
			match(IN);
			setState(186);
			expression(0);
			setState(187);
			match(COLON);
			setState(188);
			suite();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ReturnStatementContext extends ParserRuleContext {
		public TerminalNode RETURN() { return getToken(mcl_parcer.RETURN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public ReturnStatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_returnStatement; }
	}

	public final ReturnStatementContext returnStatement() throws RecognitionException {
		ReturnStatementContext _localctx = new ReturnStatementContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_returnStatement);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(190);
			match(RETURN);
			setState(192);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 4690517669502976L) != 0)) {
				{
				setState(191);
				expression(0);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExpressionContext extends ParserRuleContext {
		public ExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expression; }
	 
		public ExpressionContext() { }
		public void copyFrom(ExpressionContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LogicalOrExprContext extends ExpressionContext {
		public LogicalOrExpressionContext logicalOrExpression() {
			return getRuleContext(LogicalOrExpressionContext.class,0);
		}
		public LogicalOrExprContext(ExpressionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TernaryExpressionContext extends ExpressionContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public TerminalNode IF() { return getToken(mcl_parcer.IF, 0); }
		public TerminalNode ELSE() { return getToken(mcl_parcer.ELSE, 0); }
		public TernaryExpressionContext(ExpressionContext ctx) { copyFrom(ctx); }
	}

	public final ExpressionContext expression() throws RecognitionException {
		return expression(0);
	}

	private ExpressionContext expression(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ExpressionContext _localctx = new ExpressionContext(_ctx, _parentState);
		ExpressionContext _prevctx = _localctx;
		int _startState = 34;
		enterRecursionRule(_localctx, 34, RULE_expression, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			{
			_localctx = new LogicalOrExprContext(_localctx);
			_ctx = _localctx;
			_prevctx = _localctx;

			setState(195);
			logicalOrExpression();
			}
			_ctx.stop = _input.LT(-1);
			setState(205);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,13,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new TernaryExpressionContext(new ExpressionContext(_parentctx, _parentState));
					pushNewRecursionContext(_localctx, _startState, RULE_expression);
					setState(197);
					if (!(precpred(_ctx, 2))) throw new FailedPredicateException(this, "precpred(_ctx, 2)");
					setState(198);
					match(IF);
					setState(199);
					expression(0);
					setState(200);
					match(ELSE);
					setState(201);
					expression(2);
					}
					} 
				}
				setState(207);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,13,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalOrExpressionContext extends ParserRuleContext {
		public List<LogicalAndExpressionContext> logicalAndExpression() {
			return getRuleContexts(LogicalAndExpressionContext.class);
		}
		public LogicalAndExpressionContext logicalAndExpression(int i) {
			return getRuleContext(LogicalAndExpressionContext.class,i);
		}
		public List<TerminalNode> OR() { return getTokens(mcl_parcer.OR); }
		public TerminalNode OR(int i) {
			return getToken(mcl_parcer.OR, i);
		}
		public LogicalOrExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalOrExpression; }
	}

	public final LogicalOrExpressionContext logicalOrExpression() throws RecognitionException {
		LogicalOrExpressionContext _localctx = new LogicalOrExpressionContext(_ctx, getState());
		enterRule(_localctx, 36, RULE_logicalOrExpression);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(208);
			logicalAndExpression();
			setState(213);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(209);
					match(OR);
					setState(210);
					logicalAndExpression();
					}
					} 
				}
				setState(215);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LogicalAndExpressionContext extends ParserRuleContext {
		public List<EqualityExpressionContext> equalityExpression() {
			return getRuleContexts(EqualityExpressionContext.class);
		}
		public EqualityExpressionContext equalityExpression(int i) {
			return getRuleContext(EqualityExpressionContext.class,i);
		}
		public List<TerminalNode> AND() { return getTokens(mcl_parcer.AND); }
		public TerminalNode AND(int i) {
			return getToken(mcl_parcer.AND, i);
		}
		public LogicalAndExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_logicalAndExpression; }
	}

	public final LogicalAndExpressionContext logicalAndExpression() throws RecognitionException {
		LogicalAndExpressionContext _localctx = new LogicalAndExpressionContext(_ctx, getState());
		enterRule(_localctx, 38, RULE_logicalAndExpression);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(216);
			equalityExpression();
			setState(221);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,15,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(217);
					match(AND);
					setState(218);
					equalityExpression();
					}
					} 
				}
				setState(223);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,15,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class EqualityExpressionContext extends ParserRuleContext {
		public List<RelationalExpressionContext> relationalExpression() {
			return getRuleContexts(RelationalExpressionContext.class);
		}
		public RelationalExpressionContext relationalExpression(int i) {
			return getRuleContext(RelationalExpressionContext.class,i);
		}
		public List<TerminalNode> EQ() { return getTokens(mcl_parcer.EQ); }
		public TerminalNode EQ(int i) {
			return getToken(mcl_parcer.EQ, i);
		}
		public List<TerminalNode> NEQ() { return getTokens(mcl_parcer.NEQ); }
		public TerminalNode NEQ(int i) {
			return getToken(mcl_parcer.NEQ, i);
		}
		public EqualityExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_equalityExpression; }
	}

	public final EqualityExpressionContext equalityExpression() throws RecognitionException {
		EqualityExpressionContext _localctx = new EqualityExpressionContext(_ctx, getState());
		enterRule(_localctx, 40, RULE_equalityExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(224);
			relationalExpression();
			setState(229);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,16,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(225);
					_la = _input.LA(1);
					if ( !(_la==EQ || _la==NEQ) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(226);
					relationalExpression();
					}
					} 
				}
				setState(231);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,16,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class RelationalExpressionContext extends ParserRuleContext {
		public List<AdditiveExpressionContext> additiveExpression() {
			return getRuleContexts(AdditiveExpressionContext.class);
		}
		public AdditiveExpressionContext additiveExpression(int i) {
			return getRuleContext(AdditiveExpressionContext.class,i);
		}
		public List<TerminalNode> GT() { return getTokens(mcl_parcer.GT); }
		public TerminalNode GT(int i) {
			return getToken(mcl_parcer.GT, i);
		}
		public List<TerminalNode> LT() { return getTokens(mcl_parcer.LT); }
		public TerminalNode LT(int i) {
			return getToken(mcl_parcer.LT, i);
		}
		public List<TerminalNode> GTE() { return getTokens(mcl_parcer.GTE); }
		public TerminalNode GTE(int i) {
			return getToken(mcl_parcer.GTE, i);
		}
		public List<TerminalNode> LTE() { return getTokens(mcl_parcer.LTE); }
		public TerminalNode LTE(int i) {
			return getToken(mcl_parcer.LTE, i);
		}
		public RelationalExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_relationalExpression; }
	}

	public final RelationalExpressionContext relationalExpression() throws RecognitionException {
		RelationalExpressionContext _localctx = new RelationalExpressionContext(_ctx, getState());
		enterRule(_localctx, 42, RULE_relationalExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(232);
			additiveExpression();
			setState(237);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(233);
					_la = _input.LA(1);
					if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 1030792151040L) != 0)) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(234);
					additiveExpression();
					}
					} 
				}
				setState(239);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,17,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class AdditiveExpressionContext extends ParserRuleContext {
		public List<MultiplicativeExpressionContext> multiplicativeExpression() {
			return getRuleContexts(MultiplicativeExpressionContext.class);
		}
		public MultiplicativeExpressionContext multiplicativeExpression(int i) {
			return getRuleContext(MultiplicativeExpressionContext.class,i);
		}
		public List<TerminalNode> PLUS() { return getTokens(mcl_parcer.PLUS); }
		public TerminalNode PLUS(int i) {
			return getToken(mcl_parcer.PLUS, i);
		}
		public List<TerminalNode> MINUS() { return getTokens(mcl_parcer.MINUS); }
		public TerminalNode MINUS(int i) {
			return getToken(mcl_parcer.MINUS, i);
		}
		public AdditiveExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_additiveExpression; }
	}

	public final AdditiveExpressionContext additiveExpression() throws RecognitionException {
		AdditiveExpressionContext _localctx = new AdditiveExpressionContext(_ctx, getState());
		enterRule(_localctx, 44, RULE_additiveExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(240);
			multiplicativeExpression();
			setState(245);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(241);
					_la = _input.LA(1);
					if ( !(_la==PLUS || _la==MINUS) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(242);
					multiplicativeExpression();
					}
					} 
				}
				setState(247);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class MultiplicativeExpressionContext extends ParserRuleContext {
		public List<UnaryExpressionContext> unaryExpression() {
			return getRuleContexts(UnaryExpressionContext.class);
		}
		public UnaryExpressionContext unaryExpression(int i) {
			return getRuleContext(UnaryExpressionContext.class,i);
		}
		public List<TerminalNode> MUL() { return getTokens(mcl_parcer.MUL); }
		public TerminalNode MUL(int i) {
			return getToken(mcl_parcer.MUL, i);
		}
		public List<TerminalNode> DIV() { return getTokens(mcl_parcer.DIV); }
		public TerminalNode DIV(int i) {
			return getToken(mcl_parcer.DIV, i);
		}
		public List<TerminalNode> MOD() { return getTokens(mcl_parcer.MOD); }
		public TerminalNode MOD(int i) {
			return getToken(mcl_parcer.MOD, i);
		}
		public MultiplicativeExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_multiplicativeExpression; }
	}

	public final MultiplicativeExpressionContext multiplicativeExpression() throws RecognitionException {
		MultiplicativeExpressionContext _localctx = new MultiplicativeExpressionContext(_ctx, getState());
		enterRule(_localctx, 46, RULE_multiplicativeExpression);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(248);
			unaryExpression();
			setState(253);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,19,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					{
					{
					setState(249);
					_la = _input.LA(1);
					if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 11811160064L) != 0)) ) {
					_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(250);
					unaryExpression();
					}
					} 
				}
				setState(255);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,19,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class UnaryExpressionContext extends ParserRuleContext {
		public UnaryExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_unaryExpression; }
	 
		public UnaryExpressionContext() { }
		public void copyFrom(UnaryExpressionContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class PowerExprContext extends UnaryExpressionContext {
		public PowerExpressionContext powerExpression() {
			return getRuleContext(PowerExpressionContext.class,0);
		}
		public PowerExprContext(UnaryExpressionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class UnaryMinusPlusContext extends UnaryExpressionContext {
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public TerminalNode PLUS() { return getToken(mcl_parcer.PLUS, 0); }
		public TerminalNode MINUS() { return getToken(mcl_parcer.MINUS, 0); }
		public UnaryMinusPlusContext(UnaryExpressionContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class UnaryNotContext extends UnaryExpressionContext {
		public TerminalNode NOT() { return getToken(mcl_parcer.NOT, 0); }
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public UnaryNotContext(UnaryExpressionContext ctx) { copyFrom(ctx); }
	}

	public final UnaryExpressionContext unaryExpression() throws RecognitionException {
		UnaryExpressionContext _localctx = new UnaryExpressionContext(_ctx, getState());
		enterRule(_localctx, 48, RULE_unaryExpression);
		int _la;
		try {
			setState(261);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case PLUS:
			case MINUS:
				_localctx = new UnaryMinusPlusContext(_localctx);
				enterOuterAlt(_localctx, 1);
				{
				setState(256);
				_la = _input.LA(1);
				if ( !(_la==PLUS || _la==MINUS) ) {
				_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(257);
				unaryExpression();
				}
				break;
			case NOT:
				_localctx = new UnaryNotContext(_localctx);
				enterOuterAlt(_localctx, 2);
				{
				setState(258);
				match(NOT);
				setState(259);
				unaryExpression();
				}
				break;
			case TRUE:
			case FALSE:
			case NAN:
			case INFINITY:
			case FLOAT:
			case INTEGER:
			case STRING:
			case LPAREN:
			case LBRACE:
			case LBRACK:
			case VBAR:
			case IDENTIFIER:
				_localctx = new PowerExprContext(_localctx);
				enterOuterAlt(_localctx, 3);
				{
				setState(260);
				powerExpression();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PowerExpressionContext extends ParserRuleContext {
		public PrimaryContext primary() {
			return getRuleContext(PrimaryContext.class,0);
		}
		public TerminalNode POW() { return getToken(mcl_parcer.POW, 0); }
		public UnaryExpressionContext unaryExpression() {
			return getRuleContext(UnaryExpressionContext.class,0);
		}
		public PowerExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_powerExpression; }
	}

	public final PowerExpressionContext powerExpression() throws RecognitionException {
		PowerExpressionContext _localctx = new PowerExpressionContext(_ctx, getState());
		enterRule(_localctx, 50, RULE_powerExpression);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(263);
			primary(0);
			setState(266);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,21,_ctx) ) {
			case 1:
				{
				setState(264);
				match(POW);
				setState(265);
				unaryExpression();
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class PrimaryContext extends ParserRuleContext {
		public PrimaryContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_primary; }
	 
		public PrimaryContext() { }
		public void copyFrom(PrimaryContext ctx) {
			super.copyFrom(ctx);
		}
	}
	@SuppressWarnings("CheckReturnValue")
	public static class TypeCastContext extends PrimaryContext {
		public TerminalNode LPAREN() { return getToken(mcl_parcer.LPAREN, 0); }
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode RPAREN() { return getToken(mcl_parcer.RPAREN, 0); }
		public PrimaryContext primary() {
			return getRuleContext(PrimaryContext.class,0);
		}
		public TypeCastContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ElementAccessContext extends PrimaryContext {
		public PrimaryContext primary() {
			return getRuleContext(PrimaryContext.class,0);
		}
		public TerminalNode LBRACK() { return getToken(mcl_parcer.LBRACK, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode RBRACK() { return getToken(mcl_parcer.RBRACK, 0); }
		public ElementAccessContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class ParenthesizedExprContext extends PrimaryContext {
		public TerminalNode LPAREN() { return getToken(mcl_parcer.LPAREN, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public TerminalNode RPAREN() { return getToken(mcl_parcer.RPAREN, 0); }
		public ParenthesizedExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class LiteralExprContext extends PrimaryContext {
		public LiteralContext literal() {
			return getRuleContext(LiteralContext.class,0);
		}
		public LiteralExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class FunctionCallExprContext extends PrimaryContext {
		public FunctionCallContext functionCall() {
			return getRuleContext(FunctionCallContext.class,0);
		}
		public FunctionCallExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class CreatorExprContext extends PrimaryContext {
		public CreatorContext creator() {
			return getRuleContext(CreatorContext.class,0);
		}
		public CreatorExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class VectorLiteralExprContext extends PrimaryContext {
		public VectorLiteralContext vectorLiteral() {
			return getRuleContext(VectorLiteralContext.class,0);
		}
		public VectorLiteralExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class MatrixLiteralExprContext extends PrimaryContext {
		public MatrixLiteralContext matrixLiteral() {
			return getRuleContext(MatrixLiteralContext.class,0);
		}
		public MatrixLiteralExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class NormOrDeterminantExprContext extends PrimaryContext {
		public List<TerminalNode> VBAR() { return getTokens(mcl_parcer.VBAR); }
		public TerminalNode VBAR(int i) {
			return getToken(mcl_parcer.VBAR, i);
		}
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public NormOrDeterminantExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}
	@SuppressWarnings("CheckReturnValue")
	public static class IdentifierExprContext extends PrimaryContext {
		public TerminalNode IDENTIFIER() { return getToken(mcl_parcer.IDENTIFIER, 0); }
		public IdentifierExprContext(PrimaryContext ctx) { copyFrom(ctx); }
	}

	public final PrimaryContext primary() throws RecognitionException {
		return primary(0);
	}

	private PrimaryContext primary(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		PrimaryContext _localctx = new PrimaryContext(_ctx, _parentState);
		PrimaryContext _prevctx = _localctx;
		int _startState = 52;
		enterRecursionRule(_localctx, 52, RULE_primary, _p);
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(288);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,22,_ctx) ) {
			case 1:
				{
				_localctx = new TypeCastContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(269);
				match(LPAREN);
				setState(270);
				type();
				setState(271);
				match(RPAREN);
				setState(272);
				primary(10);
				}
				break;
			case 2:
				{
				_localctx = new LiteralExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(274);
				literal();
				}
				break;
			case 3:
				{
				_localctx = new IdentifierExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(275);
				match(IDENTIFIER);
				}
				break;
			case 4:
				{
				_localctx = new ParenthesizedExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(276);
				match(LPAREN);
				setState(277);
				expression(0);
				setState(278);
				match(RPAREN);
				}
				break;
			case 5:
				{
				_localctx = new NormOrDeterminantExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(280);
				match(VBAR);
				setState(281);
				expression(0);
				setState(282);
				match(VBAR);
				}
				break;
			case 6:
				{
				_localctx = new FunctionCallExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(284);
				functionCall();
				}
				break;
			case 7:
				{
				_localctx = new CreatorExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(285);
				creator();
				}
				break;
			case 8:
				{
				_localctx = new VectorLiteralExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(286);
				vectorLiteral();
				}
				break;
			case 9:
				{
				_localctx = new MatrixLiteralExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(287);
				matrixLiteral();
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(297);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,23,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new ElementAccessContext(new PrimaryContext(_parentctx, _parentState));
					pushNewRecursionContext(_localctx, _startState, RULE_primary);
					setState(290);
					if (!(precpred(_ctx, 1))) throw new FailedPredicateException(this, "precpred(_ctx, 1)");
					setState(291);
					match(LBRACK);
					setState(292);
					expression(0);
					setState(293);
					match(RBRACK);
					}
					} 
				}
				setState(299);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,23,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LiteralContext extends ParserRuleContext {
		public TerminalNode INTEGER() { return getToken(mcl_parcer.INTEGER, 0); }
		public TerminalNode FLOAT() { return getToken(mcl_parcer.FLOAT, 0); }
		public TerminalNode STRING() { return getToken(mcl_parcer.STRING, 0); }
		public TerminalNode TRUE() { return getToken(mcl_parcer.TRUE, 0); }
		public TerminalNode FALSE() { return getToken(mcl_parcer.FALSE, 0); }
		public TerminalNode NAN() { return getToken(mcl_parcer.NAN, 0); }
		public TerminalNode INFINITY() { return getToken(mcl_parcer.INFINITY, 0); }
		public LiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_literal; }
	}

	public final LiteralContext literal() throws RecognitionException {
		LiteralContext _localctx = new LiteralContext(_ctx, getState());
		enterRule(_localctx, 54, RULE_literal);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(300);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & 260096000L) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class VectorLiteralContext extends ParserRuleContext {
		public TerminalNode LBRACE() { return getToken(mcl_parcer.LBRACE, 0); }
		public TerminalNode RBRACE() { return getToken(mcl_parcer.RBRACE, 0); }
		public ExpressionListContext expressionList() {
			return getRuleContext(ExpressionListContext.class,0);
		}
		public VectorLiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_vectorLiteral; }
	}

	public final VectorLiteralContext vectorLiteral() throws RecognitionException {
		VectorLiteralContext _localctx = new VectorLiteralContext(_ctx, getState());
		enterRule(_localctx, 56, RULE_vectorLiteral);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(302);
			match(LBRACE);
			setState(304);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & 4690517669502976L) != 0)) {
				{
				setState(303);
				expressionList();
				}
			}

			setState(306);
			match(RBRACE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class MatrixLiteralContext extends ParserRuleContext {
		public TerminalNode LBRACE() { return getToken(mcl_parcer.LBRACE, 0); }
		public List<VectorLiteralContext> vectorLiteral() {
			return getRuleContexts(VectorLiteralContext.class);
		}
		public VectorLiteralContext vectorLiteral(int i) {
			return getRuleContext(VectorLiteralContext.class,i);
		}
		public TerminalNode RBRACE() { return getToken(mcl_parcer.RBRACE, 0); }
		public List<TerminalNode> COMMA() { return getTokens(mcl_parcer.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(mcl_parcer.COMMA, i);
		}
		public MatrixLiteralContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_matrixLiteral; }
	}

	public final MatrixLiteralContext matrixLiteral() throws RecognitionException {
		MatrixLiteralContext _localctx = new MatrixLiteralContext(_ctx, getState());
		enterRule(_localctx, 58, RULE_matrixLiteral);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(308);
			match(LBRACE);
			setState(309);
			vectorLiteral();
			setState(314);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(310);
				match(COMMA);
				setState(311);
				vectorLiteral();
				}
				}
				setState(316);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(317);
			match(RBRACE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class ExpressionListContext extends ParserRuleContext {
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(mcl_parcer.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(mcl_parcer.COMMA, i);
		}
		public ExpressionListContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expressionList; }
	}

	public final ExpressionListContext expressionList() throws RecognitionException {
		ExpressionListContext _localctx = new ExpressionListContext(_ctx, getState());
		enterRule(_localctx, 60, RULE_expressionList);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(319);
			expression(0);
			setState(324);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(320);
				match(COMMA);
				setState(321);
				expression(0);
				}
				}
				setState(326);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class CreatorContext extends ParserRuleContext {
		public List<TerminalNode> LBRACK() { return getTokens(mcl_parcer.LBRACK); }
		public TerminalNode LBRACK(int i) {
			return getToken(mcl_parcer.LBRACK, i);
		}
		public List<ExpressionContext> expression() {
			return getRuleContexts(ExpressionContext.class);
		}
		public ExpressionContext expression(int i) {
			return getRuleContext(ExpressionContext.class,i);
		}
		public List<TerminalNode> RBRACK() { return getTokens(mcl_parcer.RBRACK); }
		public TerminalNode RBRACK(int i) {
			return getToken(mcl_parcer.RBRACK, i);
		}
		public TerminalNode LPAREN() { return getToken(mcl_parcer.LPAREN, 0); }
		public TerminalNode RPAREN() { return getToken(mcl_parcer.RPAREN, 0); }
		public LambdaExpressionContext lambdaExpression() {
			return getRuleContext(LambdaExpressionContext.class,0);
		}
		public CreatorContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_creator; }
	}

	public final CreatorContext creator() throws RecognitionException {
		CreatorContext _localctx = new CreatorContext(_ctx, getState());
		enterRule(_localctx, 62, RULE_creator);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(327);
			match(LBRACK);
			setState(328);
			expression(0);
			setState(329);
			match(RBRACK);
			setState(334);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,27,_ctx) ) {
			case 1:
				{
				setState(330);
				match(LBRACK);
				setState(331);
				expression(0);
				setState(332);
				match(RBRACK);
				}
				break;
			}
			setState(343);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,29,_ctx) ) {
			case 1:
				{
				setState(336);
				match(LPAREN);
				setState(339);
				_errHandler.sync(this);
				switch (_input.LA(1)) {
				case NOT:
				case TRUE:
				case FALSE:
				case NAN:
				case INFINITY:
				case FLOAT:
				case INTEGER:
				case STRING:
				case PLUS:
				case MINUS:
				case LPAREN:
				case LBRACE:
				case LBRACK:
				case VBAR:
				case IDENTIFIER:
					{
					setState(337);
					expression(0);
					}
					break;
				case LAMBDA:
					{
					setState(338);
					lambdaExpression();
					}
					break;
				default:
					throw new NoViableAltException(this);
				}
				setState(341);
				match(RPAREN);
				}
				break;
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	@SuppressWarnings("CheckReturnValue")
	public static class LambdaExpressionContext extends ParserRuleContext {
		public TerminalNode LAMBDA() { return getToken(mcl_parcer.LAMBDA, 0); }
		public TerminalNode COLON() { return getToken(mcl_parcer.COLON, 0); }
		public ExpressionContext expression() {
			return getRuleContext(ExpressionContext.class,0);
		}
		public List<TerminalNode> IDENTIFIER() { return getTokens(mcl_parcer.IDENTIFIER); }
		public TerminalNode IDENTIFIER(int i) {
			return getToken(mcl_parcer.IDENTIFIER, i);
		}
		public List<TerminalNode> COMMA() { return getTokens(mcl_parcer.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(mcl_parcer.COMMA, i);
		}
		public LambdaExpressionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_lambdaExpression; }
	}

	public final LambdaExpressionContext lambdaExpression() throws RecognitionException {
		LambdaExpressionContext _localctx = new LambdaExpressionContext(_ctx, getState());
		enterRule(_localctx, 64, RULE_lambdaExpression);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(345);
			match(LAMBDA);
			setState(354);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==IDENTIFIER) {
				{
				setState(346);
				match(IDENTIFIER);
				setState(351);
				_errHandler.sync(this);
				_la = _input.LA(1);
				while (_la==COMMA) {
					{
					{
					setState(347);
					match(COMMA);
					setState(348);
					match(IDENTIFIER);
					}
					}
					setState(353);
					_errHandler.sync(this);
					_la = _input.LA(1);
				}
				}
			}

			setState(356);
			match(COLON);
			setState(357);
			expression(0);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 17:
			return expression_sempred((ExpressionContext)_localctx, predIndex);
		case 26:
			return primary_sempred((PrimaryContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean expression_sempred(ExpressionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 2);
		}
		return true;
	}
	private boolean primary_sempred(PrimaryContext _localctx, int predIndex) {
		switch (predIndex) {
		case 1:
			return precpred(_ctx, 1);
		}
		return true;
	}

	public static final String _serializedATN =
		"\u0004\u00019\u0168\u0002\u0000\u0007\u0000\u0002\u0001\u0007\u0001\u0002"+
		"\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002\u0004\u0007\u0004\u0002"+
		"\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002\u0007\u0007\u0007\u0002"+
		"\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0002\u000b\u0007\u000b\u0002"+
		"\f\u0007\f\u0002\r\u0007\r\u0002\u000e\u0007\u000e\u0002\u000f\u0007\u000f"+
		"\u0002\u0010\u0007\u0010\u0002\u0011\u0007\u0011\u0002\u0012\u0007\u0012"+
		"\u0002\u0013\u0007\u0013\u0002\u0014\u0007\u0014\u0002\u0015\u0007\u0015"+
		"\u0002\u0016\u0007\u0016\u0002\u0017\u0007\u0017\u0002\u0018\u0007\u0018"+
		"\u0002\u0019\u0007\u0019\u0002\u001a\u0007\u001a\u0002\u001b\u0007\u001b"+
		"\u0002\u001c\u0007\u001c\u0002\u001d\u0007\u001d\u0002\u001e\u0007\u001e"+
		"\u0002\u001f\u0007\u001f\u0002 \u0007 \u0001\u0000\u0005\u0000D\b\u0000"+
		"\n\u0000\f\u0000G\t\u0000\u0001\u0000\u0005\u0000J\b\u0000\n\u0000\f\u0000"+
		"M\t\u0000\u0001\u0000\u0001\u0000\u0001\u0001\u0001\u0001\u0001\u0001"+
		"\u0004\u0001T\b\u0001\u000b\u0001\f\u0001U\u0001\u0001\u0001\u0001\u0001"+
		"\u0002\u0001\u0002\u0001\u0002\u0001\u0002\u0003\u0002^\b\u0002\u0001"+
		"\u0002\u0001\u0002\u0001\u0002\u0001\u0002\u0001\u0002\u0001\u0002\u0001"+
		"\u0003\u0001\u0003\u0001\u0003\u0005\u0003i\b\u0003\n\u0003\f\u0003l\t"+
		"\u0003\u0001\u0004\u0001\u0004\u0001\u0004\u0001\u0004\u0001\u0005\u0001"+
		"\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0001\u0005\u0003"+
		"\u0005y\b\u0005\u0001\u0006\u0001\u0006\u0001\u0007\u0001\u0007\u0001"+
		"\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0001\b\u0003\b\u0086\b\b\u0001"+
		"\b\u0004\b\u0089\b\b\u000b\b\f\b\u008a\u0001\t\u0001\t\u0001\t\u0003\t"+
		"\u0090\b\t\u0001\t\u0001\t\u0001\t\u0001\t\u0001\n\u0001\n\u0001\n\u0003"+
		"\n\u0099\b\n\u0001\n\u0001\n\u0001\u000b\u0001\u000b\u0001\u000b\u0005"+
		"\u000b\u00a0\b\u000b\n\u000b\f\u000b\u00a3\t\u000b\u0001\f\u0001\f\u0001"+
		"\f\u0001\f\u0001\f\u0001\f\u0001\f\u0003\f\u00ac\b\f\u0001\r\u0001\r\u0001"+
		"\r\u0001\r\u0001\r\u0001\u000e\u0001\u000e\u0001\u000e\u0001\u000e\u0001"+
		"\u000e\u0001\u000f\u0001\u000f\u0001\u000f\u0001\u000f\u0001\u000f\u0001"+
		"\u000f\u0001\u000f\u0001\u0010\u0001\u0010\u0003\u0010\u00c1\b\u0010\u0001"+
		"\u0011\u0001\u0011\u0001\u0011\u0001\u0011\u0001\u0011\u0001\u0011\u0001"+
		"\u0011\u0001\u0011\u0001\u0011\u0005\u0011\u00cc\b\u0011\n\u0011\f\u0011"+
		"\u00cf\t\u0011\u0001\u0012\u0001\u0012\u0001\u0012\u0005\u0012\u00d4\b"+
		"\u0012\n\u0012\f\u0012\u00d7\t\u0012\u0001\u0013\u0001\u0013\u0001\u0013"+
		"\u0005\u0013\u00dc\b\u0013\n\u0013\f\u0013\u00df\t\u0013\u0001\u0014\u0001"+
		"\u0014\u0001\u0014\u0005\u0014\u00e4\b\u0014\n\u0014\f\u0014\u00e7\t\u0014"+
		"\u0001\u0015\u0001\u0015\u0001\u0015\u0005\u0015\u00ec\b\u0015\n\u0015"+
		"\f\u0015\u00ef\t\u0015\u0001\u0016\u0001\u0016\u0001\u0016\u0005\u0016"+
		"\u00f4\b\u0016\n\u0016\f\u0016\u00f7\t\u0016\u0001\u0017\u0001\u0017\u0001"+
		"\u0017\u0005\u0017\u00fc\b\u0017\n\u0017\f\u0017\u00ff\t\u0017\u0001\u0018"+
		"\u0001\u0018\u0001\u0018\u0001\u0018\u0001\u0018\u0003\u0018\u0106\b\u0018"+
		"\u0001\u0019\u0001\u0019\u0001\u0019\u0003\u0019\u010b\b\u0019\u0001\u001a"+
		"\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a"+
		"\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a"+
		"\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a\u0001\u001a"+
		"\u0001\u001a\u0003\u001a\u0121\b\u001a\u0001\u001a\u0001\u001a\u0001\u001a"+
		"\u0001\u001a\u0001\u001a\u0005\u001a\u0128\b\u001a\n\u001a\f\u001a\u012b"+
		"\t\u001a\u0001\u001b\u0001\u001b\u0001\u001c\u0001\u001c\u0003\u001c\u0131"+
		"\b\u001c\u0001\u001c\u0001\u001c\u0001\u001d\u0001\u001d\u0001\u001d\u0001"+
		"\u001d\u0005\u001d\u0139\b\u001d\n\u001d\f\u001d\u013c\t\u001d\u0001\u001d"+
		"\u0001\u001d\u0001\u001e\u0001\u001e\u0001\u001e\u0005\u001e\u0143\b\u001e"+
		"\n\u001e\f\u001e\u0146\t\u001e\u0001\u001f\u0001\u001f\u0001\u001f\u0001"+
		"\u001f\u0001\u001f\u0001\u001f\u0001\u001f\u0003\u001f\u014f\b\u001f\u0001"+
		"\u001f\u0001\u001f\u0001\u001f\u0003\u001f\u0154\b\u001f\u0001\u001f\u0001"+
		"\u001f\u0003\u001f\u0158\b\u001f\u0001 \u0001 \u0001 \u0001 \u0005 \u015e"+
		"\b \n \f \u0161\t \u0003 \u0163\b \u0001 \u0001 \u0001 \u0001 \u0000\u0002"+
		"\"4!\u0000\u0002\u0004\u0006\b\n\f\u000e\u0010\u0012\u0014\u0016\u0018"+
		"\u001a\u001c\u001e \"$&(*,.02468:<>@\u0000\u0006\u0001\u0000\u0010\u0011"+
		"\u0001\u0000\"#\u0001\u0000$\'\u0001\u0000\u001c\u001d\u0002\u0000\u001e"+
		"\u001f!!\u0002\u0000\u000e\u000f\u0017\u001b\u0178\u0000E\u0001\u0000"+
		"\u0000\u0000\u0002P\u0001\u0000\u0000\u0000\u0004Y\u0001\u0000\u0000\u0000"+
		"\u0006e\u0001\u0000\u0000\u0000\bm\u0001\u0000\u0000\u0000\nx\u0001\u0000"+
		"\u0000\u0000\fz\u0001\u0000\u0000\u0000\u000e|\u0001\u0000\u0000\u0000"+
		"\u0010\u0085\u0001\u0000\u0000\u0000\u0012\u008f\u0001\u0000\u0000\u0000"+
		"\u0014\u0095\u0001\u0000\u0000\u0000\u0016\u009c\u0001\u0000\u0000\u0000"+
		"\u0018\u00a4\u0001\u0000\u0000\u0000\u001a\u00ad\u0001\u0000\u0000\u0000"+
		"\u001c\u00b2\u0001\u0000\u0000\u0000\u001e\u00b7\u0001\u0000\u0000\u0000"+
		" \u00be\u0001\u0000\u0000\u0000\"\u00c2\u0001\u0000\u0000\u0000$\u00d0"+
		"\u0001\u0000\u0000\u0000&\u00d8\u0001\u0000\u0000\u0000(\u00e0\u0001\u0000"+
		"\u0000\u0000*\u00e8\u0001\u0000\u0000\u0000,\u00f0\u0001\u0000\u0000\u0000"+
		".\u00f8\u0001\u0000\u0000\u00000\u0105\u0001\u0000\u0000\u00002\u0107"+
		"\u0001\u0000\u0000\u00004\u0120\u0001\u0000\u0000\u00006\u012c\u0001\u0000"+
		"\u0000\u00008\u012e\u0001\u0000\u0000\u0000:\u0134\u0001\u0000\u0000\u0000"+
		"<\u013f\u0001\u0000\u0000\u0000>\u0147\u0001\u0000\u0000\u0000@\u0159"+
		"\u0001\u0000\u0000\u0000BD\u0003\u0004\u0002\u0000CB\u0001\u0000\u0000"+
		"\u0000DG\u0001\u0000\u0000\u0000EC\u0001\u0000\u0000\u0000EF\u0001\u0000"+
		"\u0000\u0000FK\u0001\u0000\u0000\u0000GE\u0001\u0000\u0000\u0000HJ\u0003"+
		"\u0010\b\u0000IH\u0001\u0000\u0000\u0000JM\u0001\u0000\u0000\u0000KI\u0001"+
		"\u0000\u0000\u0000KL\u0001\u0000\u0000\u0000LN\u0001\u0000\u0000\u0000"+
		"MK\u0001\u0000\u0000\u0000NO\u0005\u0000\u0000\u0001O\u0001\u0001\u0000"+
		"\u0000\u0000PQ\u00057\u0000\u0000QS\u00058\u0000\u0000RT\u0003\u0010\b"+
		"\u0000SR\u0001\u0000\u0000\u0000TU\u0001\u0000\u0000\u0000US\u0001\u0000"+
		"\u0000\u0000UV\u0001\u0000\u0000\u0000VW\u0001\u0000\u0000\u0000WX\u0005"+
		"9\u0000\u0000X\u0003\u0001\u0000\u0000\u0000YZ\u0005\u0007\u0000\u0000"+
		"Z[\u00054\u0000\u0000[]\u0005)\u0000\u0000\\^\u0003\u0006\u0003\u0000"+
		"]\\\u0001\u0000\u0000\u0000]^\u0001\u0000\u0000\u0000^_\u0001\u0000\u0000"+
		"\u0000_`\u0005*\u0000\u0000`a\u00052\u0000\u0000ab\u0003\n\u0005\u0000"+
		"bc\u00051\u0000\u0000cd\u0003\u0002\u0001\u0000d\u0005\u0001\u0000\u0000"+
		"\u0000ej\u0003\b\u0004\u0000fg\u00050\u0000\u0000gi\u0003\b\u0004\u0000"+
		"hf\u0001\u0000\u0000\u0000il\u0001\u0000\u0000\u0000jh\u0001\u0000\u0000"+
		"\u0000jk\u0001\u0000\u0000\u0000k\u0007\u0001\u0000\u0000\u0000lj\u0001"+
		"\u0000\u0000\u0000mn\u00054\u0000\u0000no\u00051\u0000\u0000op\u0003\n"+
		"\u0005\u0000p\t\u0001\u0000\u0000\u0000qy\u0003\f\u0006\u0000ry\u0003"+
		"\u000e\u0007\u0000sy\u0005\u0013\u0000\u0000ty\u0005\u0014\u0000\u0000"+
		"uy\u0005\u0015\u0000\u0000vy\u0005\u0016\u0000\u0000wy\u0005\t\u0000\u0000"+
		"xq\u0001\u0000\u0000\u0000xr\u0001\u0000\u0000\u0000xs\u0001\u0000\u0000"+
		"\u0000xt\u0001\u0000\u0000\u0000xu\u0001\u0000\u0000\u0000xv\u0001\u0000"+
		"\u0000\u0000xw\u0001\u0000\u0000\u0000y\u000b\u0001\u0000\u0000\u0000"+
		"z{\u0007\u0000\u0000\u0000{\r\u0001\u0000\u0000\u0000|}\u0005\u0012\u0000"+
		"\u0000}\u000f\u0001\u0000\u0000\u0000~\u0086\u0003\u0012\t\u0000\u007f"+
		"\u0086\u0003\u0014\n\u0000\u0080\u0086\u0003\u0018\f\u0000\u0081\u0086"+
		"\u0003\u001a\r\u0000\u0082\u0086\u0003\u001c\u000e\u0000\u0083\u0086\u0003"+
		"\u001e\u000f\u0000\u0084\u0086\u0003 \u0010\u0000\u0085~\u0001\u0000\u0000"+
		"\u0000\u0085\u007f\u0001\u0000\u0000\u0000\u0085\u0080\u0001\u0000\u0000"+
		"\u0000\u0085\u0081\u0001\u0000\u0000\u0000\u0085\u0082\u0001\u0000\u0000"+
		"\u0000\u0085\u0083\u0001\u0000\u0000\u0000\u0085\u0084\u0001\u0000\u0000"+
		"\u0000\u0086\u0088\u0001\u0000\u0000\u0000\u0087\u0089\u00057\u0000\u0000"+
		"\u0088\u0087\u0001\u0000\u0000\u0000\u0089\u008a\u0001\u0000\u0000\u0000"+
		"\u008a\u0088\u0001\u0000\u0000\u0000\u008a\u008b\u0001\u0000\u0000\u0000"+
		"\u008b\u0011\u0001\u0000\u0000\u0000\u008c\u008d\u0003\n\u0005\u0000\u008d"+
		"\u008e\u00053\u0000\u0000\u008e\u0090\u0001\u0000\u0000\u0000\u008f\u008c"+
		"\u0001\u0000\u0000\u0000\u008f\u0090\u0001\u0000\u0000\u0000\u0090\u0091"+
		"\u0001\u0000\u0000\u0000\u0091\u0092\u00054\u0000\u0000\u0092\u0093\u0005"+
		"(\u0000\u0000\u0093\u0094\u0003\"\u0011\u0000\u0094\u0013\u0001\u0000"+
		"\u0000\u0000\u0095\u0096\u00054\u0000\u0000\u0096\u0098\u0005)\u0000\u0000"+
		"\u0097\u0099\u0003\u0016\u000b\u0000\u0098\u0097\u0001\u0000\u0000\u0000"+
		"\u0098\u0099\u0001\u0000\u0000\u0000\u0099\u009a\u0001\u0000\u0000\u0000"+
		"\u009a\u009b\u0005*\u0000\u0000\u009b\u0015\u0001\u0000\u0000\u0000\u009c"+
		"\u00a1\u0003\"\u0011\u0000\u009d\u009e\u00050\u0000\u0000\u009e\u00a0"+
		"\u0003\"\u0011\u0000\u009f\u009d\u0001\u0000\u0000\u0000\u00a0\u00a3\u0001"+
		"\u0000\u0000\u0000\u00a1\u009f\u0001\u0000\u0000\u0000\u00a1\u00a2\u0001"+
		"\u0000\u0000\u0000\u00a2\u0017\u0001\u0000\u0000\u0000\u00a3\u00a1\u0001"+
		"\u0000\u0000\u0000\u00a4\u00a5\u0005\u0001\u0000\u0000\u00a5\u00a6\u0003"+
		"\"\u0011\u0000\u00a6\u00a7\u00051\u0000\u0000\u00a7\u00ab\u0003\u0002"+
		"\u0001\u0000\u00a8\u00a9\u0005\u0002\u0000\u0000\u00a9\u00aa\u00051\u0000"+
		"\u0000\u00aa\u00ac\u0003\u0002\u0001\u0000\u00ab\u00a8\u0001\u0000\u0000"+
		"\u0000\u00ab\u00ac\u0001\u0000\u0000\u0000\u00ac\u0019\u0001\u0000\u0000"+
		"\u0000\u00ad\u00ae\u0005\u0003\u0000\u0000\u00ae\u00af\u0003\"\u0011\u0000"+
		"\u00af\u00b0\u00051\u0000\u0000\u00b0\u00b1\u0003\u0002\u0001\u0000\u00b1"+
		"\u001b\u0001\u0000\u0000\u0000\u00b2\u00b3\u0005\u0004\u0000\u0000\u00b3"+
		"\u00b4\u0003\"\u0011\u0000\u00b4\u00b5\u00051\u0000\u0000\u00b5\u00b6"+
		"\u0003\u0002\u0001\u0000\u00b6\u001d\u0001\u0000\u0000\u0000\u00b7\u00b8"+
		"\u0005\u0005\u0000\u0000\u00b8\u00b9\u00054\u0000\u0000\u00b9\u00ba\u0005"+
		"\u0006\u0000\u0000\u00ba\u00bb\u0003\"\u0011\u0000\u00bb\u00bc\u00051"+
		"\u0000\u0000\u00bc\u00bd\u0003\u0002\u0001\u0000\u00bd\u001f\u0001\u0000"+
		"\u0000\u0000\u00be\u00c0\u0005\b\u0000\u0000\u00bf\u00c1\u0003\"\u0011"+
		"\u0000\u00c0\u00bf\u0001\u0000\u0000\u0000\u00c0\u00c1\u0001\u0000\u0000"+
		"\u0000\u00c1!\u0001\u0000\u0000\u0000\u00c2\u00c3\u0006\u0011\uffff\uffff"+
		"\u0000\u00c3\u00c4\u0003$\u0012\u0000\u00c4\u00cd\u0001\u0000\u0000\u0000"+
		"\u00c5\u00c6\n\u0002\u0000\u0000\u00c6\u00c7\u0005\u0001\u0000\u0000\u00c7"+
		"\u00c8\u0003\"\u0011\u0000\u00c8\u00c9\u0005\u0002\u0000\u0000\u00c9\u00ca"+
		"\u0003\"\u0011\u0002\u00ca\u00cc\u0001\u0000\u0000\u0000\u00cb\u00c5\u0001"+
		"\u0000\u0000\u0000\u00cc\u00cf\u0001\u0000\u0000\u0000\u00cd\u00cb\u0001"+
		"\u0000\u0000\u0000\u00cd\u00ce\u0001\u0000\u0000\u0000\u00ce#\u0001\u0000"+
		"\u0000\u0000\u00cf\u00cd\u0001\u0000\u0000\u0000\u00d0\u00d5\u0003&\u0013"+
		"\u0000\u00d1\u00d2\u0005\f\u0000\u0000\u00d2\u00d4\u0003&\u0013\u0000"+
		"\u00d3\u00d1\u0001\u0000\u0000\u0000\u00d4\u00d7\u0001\u0000\u0000\u0000"+
		"\u00d5\u00d3\u0001\u0000\u0000\u0000\u00d5\u00d6\u0001\u0000\u0000\u0000"+
		"\u00d6%\u0001\u0000\u0000\u0000\u00d7\u00d5\u0001\u0000\u0000\u0000\u00d8"+
		"\u00dd\u0003(\u0014\u0000\u00d9\u00da\u0005\u000b\u0000\u0000\u00da\u00dc"+
		"\u0003(\u0014\u0000\u00db\u00d9\u0001\u0000\u0000\u0000\u00dc\u00df\u0001"+
		"\u0000\u0000\u0000\u00dd\u00db\u0001\u0000\u0000\u0000\u00dd\u00de\u0001"+
		"\u0000\u0000\u0000\u00de\'\u0001\u0000\u0000\u0000\u00df\u00dd\u0001\u0000"+
		"\u0000\u0000\u00e0\u00e5\u0003*\u0015\u0000\u00e1\u00e2\u0007\u0001\u0000"+
		"\u0000\u00e2\u00e4\u0003*\u0015\u0000\u00e3\u00e1\u0001\u0000\u0000\u0000"+
		"\u00e4\u00e7\u0001\u0000\u0000\u0000\u00e5\u00e3\u0001\u0000\u0000\u0000"+
		"\u00e5\u00e6\u0001\u0000\u0000\u0000\u00e6)\u0001\u0000\u0000\u0000\u00e7"+
		"\u00e5\u0001\u0000\u0000\u0000\u00e8\u00ed\u0003,\u0016\u0000\u00e9\u00ea"+
		"\u0007\u0002\u0000\u0000\u00ea\u00ec\u0003,\u0016\u0000\u00eb\u00e9\u0001"+
		"\u0000\u0000\u0000\u00ec\u00ef\u0001\u0000\u0000\u0000\u00ed\u00eb\u0001"+
		"\u0000\u0000\u0000\u00ed\u00ee\u0001\u0000\u0000\u0000\u00ee+\u0001\u0000"+
		"\u0000\u0000\u00ef\u00ed\u0001\u0000\u0000\u0000\u00f0\u00f5\u0003.\u0017"+
		"\u0000\u00f1\u00f2\u0007\u0003\u0000\u0000\u00f2\u00f4\u0003.\u0017\u0000"+
		"\u00f3\u00f1\u0001\u0000\u0000\u0000\u00f4\u00f7\u0001\u0000\u0000\u0000"+
		"\u00f5\u00f3\u0001\u0000\u0000\u0000\u00f5\u00f6\u0001\u0000\u0000\u0000"+
		"\u00f6-\u0001\u0000\u0000\u0000\u00f7\u00f5\u0001\u0000\u0000\u0000\u00f8"+
		"\u00fd\u00030\u0018\u0000\u00f9\u00fa\u0007\u0004\u0000\u0000\u00fa\u00fc"+
		"\u00030\u0018\u0000\u00fb\u00f9\u0001\u0000\u0000\u0000\u00fc\u00ff\u0001"+
		"\u0000\u0000\u0000\u00fd\u00fb\u0001\u0000\u0000\u0000\u00fd\u00fe\u0001"+
		"\u0000\u0000\u0000\u00fe/\u0001\u0000\u0000\u0000\u00ff\u00fd\u0001\u0000"+
		"\u0000\u0000\u0100\u0101\u0007\u0003\u0000\u0000\u0101\u0106\u00030\u0018"+
		"\u0000\u0102\u0103\u0005\r\u0000\u0000\u0103\u0106\u00030\u0018\u0000"+
		"\u0104\u0106\u00032\u0019\u0000\u0105\u0100\u0001\u0000\u0000\u0000\u0105"+
		"\u0102\u0001\u0000\u0000\u0000\u0105\u0104\u0001\u0000\u0000\u0000\u0106"+
		"1\u0001\u0000\u0000\u0000\u0107\u010a\u00034\u001a\u0000\u0108\u0109\u0005"+
		" \u0000\u0000\u0109\u010b\u00030\u0018\u0000\u010a\u0108\u0001\u0000\u0000"+
		"\u0000\u010a\u010b\u0001\u0000\u0000\u0000\u010b3\u0001\u0000\u0000\u0000"+
		"\u010c\u010d\u0006\u001a\uffff\uffff\u0000\u010d\u010e\u0005)\u0000\u0000"+
		"\u010e\u010f\u0003\n\u0005\u0000\u010f\u0110\u0005*\u0000\u0000\u0110"+
		"\u0111\u00034\u001a\n\u0111\u0121\u0001\u0000\u0000\u0000\u0112\u0121"+
		"\u00036\u001b\u0000\u0113\u0121\u00054\u0000\u0000\u0114\u0115\u0005)"+
		"\u0000\u0000\u0115\u0116\u0003\"\u0011\u0000\u0116\u0117\u0005*\u0000"+
		"\u0000\u0117\u0121\u0001\u0000\u0000\u0000\u0118\u0119\u0005/\u0000\u0000"+
		"\u0119\u011a\u0003\"\u0011\u0000\u011a\u011b\u0005/\u0000\u0000\u011b"+
		"\u0121\u0001\u0000\u0000\u0000\u011c\u0121\u0003\u0014\n\u0000\u011d\u0121"+
		"\u0003>\u001f\u0000\u011e\u0121\u00038\u001c\u0000\u011f\u0121\u0003:"+
		"\u001d\u0000\u0120\u010c\u0001\u0000\u0000\u0000\u0120\u0112\u0001\u0000"+
		"\u0000\u0000\u0120\u0113\u0001\u0000\u0000\u0000\u0120\u0114\u0001\u0000"+
		"\u0000\u0000\u0120\u0118\u0001\u0000\u0000\u0000\u0120\u011c\u0001\u0000"+
		"\u0000\u0000\u0120\u011d\u0001\u0000\u0000\u0000\u0120\u011e\u0001\u0000"+
		"\u0000\u0000\u0120\u011f\u0001\u0000\u0000\u0000\u0121\u0129\u0001\u0000"+
		"\u0000\u0000\u0122\u0123\n\u0001\u0000\u0000\u0123\u0124\u0005-\u0000"+
		"\u0000\u0124\u0125\u0003\"\u0011\u0000\u0125\u0126\u0005.\u0000\u0000"+
		"\u0126\u0128\u0001\u0000\u0000\u0000\u0127\u0122\u0001\u0000\u0000\u0000"+
		"\u0128\u012b\u0001\u0000\u0000\u0000\u0129\u0127\u0001\u0000\u0000\u0000"+
		"\u0129\u012a\u0001\u0000\u0000\u0000\u012a5\u0001\u0000\u0000\u0000\u012b"+
		"\u0129\u0001\u0000\u0000\u0000\u012c\u012d\u0007\u0005\u0000\u0000\u012d"+
		"7\u0001\u0000\u0000\u0000\u012e\u0130\u0005+\u0000\u0000\u012f\u0131\u0003"+
		"<\u001e\u0000\u0130\u012f\u0001\u0000\u0000\u0000\u0130\u0131\u0001\u0000"+
		"\u0000\u0000\u0131\u0132\u0001\u0000\u0000\u0000\u0132\u0133\u0005,\u0000"+
		"\u0000\u01339\u0001\u0000\u0000\u0000\u0134\u0135\u0005+\u0000\u0000\u0135"+
		"\u013a\u00038\u001c\u0000\u0136\u0137\u00050\u0000\u0000\u0137\u0139\u0003"+
		"8\u001c\u0000\u0138\u0136\u0001\u0000\u0000\u0000\u0139\u013c\u0001\u0000"+
		"\u0000\u0000\u013a\u0138\u0001\u0000\u0000\u0000\u013a\u013b\u0001\u0000"+
		"\u0000\u0000\u013b\u013d\u0001\u0000\u0000\u0000\u013c\u013a\u0001\u0000"+
		"\u0000\u0000\u013d\u013e\u0005,\u0000\u0000\u013e;\u0001\u0000\u0000\u0000"+
		"\u013f\u0144\u0003\"\u0011\u0000\u0140\u0141\u00050\u0000\u0000\u0141"+
		"\u0143\u0003\"\u0011\u0000\u0142\u0140\u0001\u0000\u0000\u0000\u0143\u0146"+
		"\u0001\u0000\u0000\u0000\u0144\u0142\u0001\u0000\u0000\u0000\u0144\u0145"+
		"\u0001\u0000\u0000\u0000\u0145=\u0001\u0000\u0000\u0000\u0146\u0144\u0001"+
		"\u0000\u0000\u0000\u0147\u0148\u0005-\u0000\u0000\u0148\u0149\u0003\""+
		"\u0011\u0000\u0149\u014e\u0005.\u0000\u0000\u014a\u014b\u0005-\u0000\u0000"+
		"\u014b\u014c\u0003\"\u0011\u0000\u014c\u014d\u0005.\u0000\u0000\u014d"+
		"\u014f\u0001\u0000\u0000\u0000\u014e\u014a\u0001\u0000\u0000\u0000\u014e"+
		"\u014f\u0001\u0000\u0000\u0000\u014f\u0157\u0001\u0000\u0000\u0000\u0150"+
		"\u0153\u0005)\u0000\u0000\u0151\u0154\u0003\"\u0011\u0000\u0152\u0154"+
		"\u0003@ \u0000\u0153\u0151\u0001\u0000\u0000\u0000\u0153\u0152\u0001\u0000"+
		"\u0000\u0000\u0154\u0155\u0001\u0000\u0000\u0000\u0155\u0156\u0005*\u0000"+
		"\u0000\u0156\u0158\u0001\u0000\u0000\u0000\u0157\u0150\u0001\u0000\u0000"+
		"\u0000\u0157\u0158\u0001\u0000\u0000\u0000\u0158?\u0001\u0000\u0000\u0000"+
		"\u0159\u0162\u0005\n\u0000\u0000\u015a\u015f\u00054\u0000\u0000\u015b"+
		"\u015c\u00050\u0000\u0000\u015c\u015e\u00054\u0000\u0000\u015d\u015b\u0001"+
		"\u0000\u0000\u0000\u015e\u0161\u0001\u0000\u0000\u0000\u015f\u015d\u0001"+
		"\u0000\u0000\u0000\u015f\u0160\u0001\u0000\u0000\u0000\u0160\u0163\u0001"+
		"\u0000\u0000\u0000\u0161\u015f\u0001\u0000\u0000\u0000\u0162\u015a\u0001"+
		"\u0000\u0000\u0000\u0162\u0163\u0001\u0000\u0000\u0000\u0163\u0164\u0001"+
		"\u0000\u0000\u0000\u0164\u0165\u00051\u0000\u0000\u0165\u0166\u0003\""+
		"\u0011\u0000\u0166A\u0001\u0000\u0000\u0000 EKU]jx\u0085\u008a\u008f\u0098"+
		"\u00a1\u00ab\u00c0\u00cd\u00d5\u00dd\u00e5\u00ed\u00f5\u00fd\u0105\u010a"+
		"\u0120\u0129\u0130\u013a\u0144\u014e\u0153\u0157\u015f\u0162";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}