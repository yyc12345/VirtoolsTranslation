import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.util.Stack;
import java.util.List;
import java.lang.StringBuilder;

public class NlpRunner {
	public static class ConvertToJson extends NlpBaseListener {
		public ConvertToJson() {
			mIndent = 0;
			
			mEntryIndex = 0;
			mEntryIndexStack = new Stack<Integer>();
			mIsFirst = true;
			mIsFirstStack = new Stack<Boolean>();
		}
		
		private String cutLangHead(String strl) {
			return strl.substring("Language:".length());
		}
		private String cutSectionHead(String strl) {
			return strl.substring(1, strl.length() - 1);
		}
		private String cutString(String strl) {
			return strl.substring(1, strl.length() - 1);
		}
		private String joinConcatedString(List<TerminalNode> ls) {
			StringBuilder sb = new StringBuilder();
			for (TerminalNode node : ls) {
				sb.append(cutString(node.getText()));
			}
			
			return sb.toString();
		}
		
		int mEntryIndex;
		boolean mIsFirst;
		Stack<Integer> mEntryIndexStack;
		Stack<Boolean> mIsFirstStack;
		private void pushSection() {
			mEntryIndexStack.push(mEntryIndex);
			mEntryIndex = 0;
			mIsFirstStack.push(mIsFirst);
			mIsFirst = true;
		}
		private void popSection() {
			mEntryIndex = mEntryIndexStack.pop();
			mIsFirst = mIsFirstStack.pop();
		}
		private void printComma() {
			// only the first entry do not need comma
			if (mIsFirst) {
				mIsFirst = false;
			} else {
				System.out.print(',');
			}
		}
		
		int mIndent;
		private void printIndent() {
			for(int i = 0; i < mIndent; ++i) {
				System.out.print('\t');
			}
		}
		private void printEOL() {
			System.out.print('\n');
		}
		private void printIndentLn(String strl) {
			// call this when writting tail bracket
			printEOL();
			printIndent();
			System.out.print(strl);
		}
		private void printIndentCommaLn(String strl) {
			// call this when writting anything else.
			printComma();
			printEOL();
			printIndent();
			System.out.print(strl);
		}
		
		private void printStrEntry(String val) {
			printIndentCommaLn(String.format("\"%s\": \"%s\"", mEntryIndex++, val));
		}
		private void printIntEntry(int val) {
			printIndentCommaLn(String.format("\"%s\": %d", mEntryIndex++, val));
		}

		
		@Override
		public void enterDocument(NlpParser.DocumentContext ctx) {
			printIndentCommaLn("{");
			pushSection();
			++mIndent;
			
			printIndentCommaLn(String.format("\"Language\": \"%s\"", cutLangHead(ctx.LANG_HEADER().getText())));
			
			printIndentCommaLn("\"document\": {");
			pushSection();
			++mIndent;
		}
		@Override
		public void exitDocument(NlpParser.DocumentContext ctx) {
			--mIndent;
			popSection();
			printIndentLn("}");
			
			--mIndent;
			popSection();
			printIndentLn("}");
		}
		
		@Override 
		public void enterSection(NlpParser.SectionContext ctx) { 
			printIndentCommaLn(String.format("\"%s\": {", cutSectionHead(ctx.SECTION_HEAD().getText())));
			pushSection();
			++mIndent;
		}
		@Override 
		public void exitSection(NlpParser.SectionContext ctx) { 
			--mIndent;
			popSection();
			printIndentLn("}");
		}
		
		@Override 
		public void enterSubSection(NlpParser.SubSectionContext ctx) { 
			printIndentCommaLn(String.format("\"%s\": {", cutSectionHead(ctx.SUB_SECTION_HEAD().getText())));
			pushSection();
			++mIndent;
		}
		@Override 
		public void exitSubSection(NlpParser.SubSectionContext ctx) {
			--mIndent;
			popSection();
			printIndentLn("}");
		}
		
		@Override 
		public void enterEntryString(NlpParser.EntryStringContext ctx) {
			printStrEntry(cutString(ctx.ENTRY_STRING().getText()));
		}
		@Override 
		public void enterEntryConcatedString(NlpParser.EntryConcatedStringContext ctx) {
			printStrEntry(joinConcatedString(ctx.ENTRY_STRING()));
		}
		@Override 
		public void enterEntryInteger(NlpParser.EntryIntegerContext ctx) { 
			printIntEntry(Integer.parseInt(ctx.ENTRY_INTEGER().getText()));
		}
	}
	
	public static void main(String[] args) throws Exception {
		ANTLRInputStream input = new ANTLRInputStream(System.in);
		NlpLexer lexer = new NlpLexer(input);
		CommonTokenStream tokens = new CommonTokenStream(lexer);
		NlpParser parser = new NlpParser(tokens);
		
		ParseTree tree = parser.document();
		ParseTreeWalker walker = new ParseTreeWalker();
		walker.walk(new ConvertToJson(), tree);
		System.out.println();
	}
}
