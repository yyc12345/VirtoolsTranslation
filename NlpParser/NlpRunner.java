// import antlr stuff
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
// import container
import java.util.Stack;
import java.util.stream.Collectors;
import java.util.List;
import java.lang.StringBuilder;
// import json
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
// import regex
import java.util.regex.Pattern;
import java.util.regex.Matcher;

public class NlpRunner {
	public static class NlpJsonConverter extends NlpBaseListener {
		public NlpJsonConverter() {
			mGsonInstance = new GsonBuilder().setPrettyPrinting().create();
			mRoot = new JsonObject();
			mSection = new JsonArray();
			mSectionStack = new Stack<JsonArray>();
		}
		/* JSON related stuff */
		
		Gson mGsonInstance;
		public void printJson() {
			System.out.print(mGsonInstance.toJson(mRoot));;
		}
		
		/* String related stuff */
		
		private static final Pattern mRegStrCctor = Pattern.compile("\\\\[^\\r\\n]*[\\r\\n]+");
		private static final Pattern mRegDoubleQuote = Pattern.compile("\\\"\\\"");
		private static final Pattern mRegEscTab = Pattern.compile("\\t");
		private static final Pattern mRegEscEol = Pattern.compile("\\r?\\n");
		private String cutLangHead(String strl) {
			return strl.substring("Language:".length());
		}
		private String cutSectionHead(String strl) {
			return strl.substring(1, strl.length() - 1);
		}
		private String cutString(String strl) {
			return strl.substring(1, strl.length() - 1);
		}
		private String regulateString(String strl) {
			strl = mRegStrCctor.matcher(strl).replaceAll(Matcher.quoteReplacement(""));		// remove string concator \\[^\r\n]*[\r\n]+
			strl = mRegDoubleQuote.matcher(strl).replaceAll(Matcher.quoteReplacement("\""));// replace "" with "
			strl = mRegEscTab.matcher(strl).replaceAll(Matcher.quoteReplacement("\\t"));	// replace real \t to escape char
			strl = mRegEscEol.matcher(strl).replaceAll(Matcher.quoteReplacement("\\n"));	// replace all real \n to escape char
			
			return strl;			
		}
		private String processString(String strl) {
			return regulateString(cutString(strl));
		}
		private String processConcatedString(List<String> ls) {
			StringBuilder sb = new StringBuilder();
			for (String node : ls) {
				sb.append(regulateString(cutString(node)));
			}
			
			return sb.toString();
		}
		
		/* Section layout related stuff */
		
		JsonObject mRoot;
		JsonArray mSection;
		Stack<JsonArray> mSectionStack;
		private void pushSection() {
			mSectionStack.push(mSection);
			mSection = new JsonArray();
		}
		private void popSection() {
			mSection = mSectionStack.pop();
		}
		
		/* Listener */
		
		@Override
		public void enterDocument(NlpParser.DocumentContext ctx) {
			// insert language prop
			mRoot.addProperty("language", cutLangHead(ctx.LANG_HEADER().getText()));
		}
		@Override
		public void exitDocument(NlpParser.DocumentContext ctx) {
			// insert document prop
			mRoot.add("entries", mSection);
		}
		
		@Override 
		public void enterSection(NlpParser.SectionContext ctx) { 
			pushSection();
		}
		@Override 
		public void exitSection(NlpParser.SectionContext ctx) { 
			// create new object
			JsonObject objSection = new JsonObject();
			objSection.addProperty("section", cutSectionHead(ctx.SECTION_HEAD().getText()));
			objSection.add("entries", mSection);
			// pop and insert
			popSection();
			mSection.add(objSection);
		}
		
		@Override 
		public void enterSubSection(NlpParser.SubSectionContext ctx) { 
			pushSection();
		}
		@Override 
		public void exitSubSection(NlpParser.SubSectionContext ctx) {
			// create new object
			JsonObject objSubSection = new JsonObject();
			objSubSection.addProperty("section", cutSectionHead(ctx.SUB_SECTION_HEAD().getText()));
			objSubSection.add("entries", mSection);
			// pop and insert
			popSection();
			mSection.add(objSubSection);
		}
		
		@Override 
		public void enterEntryString(NlpParser.EntryStringContext ctx) {
			mSection.add(processString(ctx.ENTRY_STRING().getText()));
		}
		@Override 
		public void enterEntryConcatedString(NlpParser.EntryConcatedStringContext ctx) {
			mSection.add(processConcatedString(
					ctx.ENTRY_STRING().stream().map(value -> value.getText()).collect(Collectors.toList())
					));
		}
		@Override 
		public void enterEntryInteger(NlpParser.EntryIntegerContext ctx) { 
			mSection.add(Integer.parseInt(ctx.ENTRY_INTEGER().getText()));
		}
	}
	
	public static void main(String[] args) throws Exception {
		ANTLRInputStream input = new ANTLRInputStream(System.in);
		NlpLexer lexer = new NlpLexer(input);
		CommonTokenStream tokens = new CommonTokenStream(lexer);
		NlpParser parser = new NlpParser(tokens);
		
		ParseTree tree = parser.document();
		ParseTreeWalker walker = new ParseTreeWalker();
		NlpJsonConverter converter = new NlpJsonConverter();
		walker.walk(converter, tree);
		converter.printJson();
		System.out.println();
	}
}
