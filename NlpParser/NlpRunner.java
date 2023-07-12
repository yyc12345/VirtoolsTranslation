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
// import io related
import java.io.FileOutputStream;
import java.io.FileInputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class NlpRunner {
	public static class NlpJsonConverter extends NlpBaseListener {
		public NlpJsonConverter() {
			mGsonInstance = new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
			mRoot = new JsonObject();
			mSection = new JsonArray();
			mSectionStack = new Stack<JsonArray>();
		}
		/* JSON related stuff */
		
		Gson mGsonInstance;
		public String buildJsonString() {
			return mGsonInstance.toJson(mRoot);
		}
		
		/* String related stuff */
		
		// \\\\[^\\rn] match the concator. concator must not be appended with \n \r or \\ 
		// [^\\r\\n]*[\\r\\n]+ is match to line breaker.
		private static final Pattern mRegStrCctor = Pattern.compile("\\\\[^\\\\rn][^\\r\\n]*[\\r\\n]+");
		private static final Pattern mRegDoubleQuote = Pattern.compile("\\\"\\\"");
		// private static final Pattern mRegEscSlash = Pattern.compile("\\\\\\\\");
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
			strl = mRegStrCctor.matcher(strl).replaceAll(Matcher.quoteReplacement(""));		// remove string concator
			strl = mRegDoubleQuote.matcher(strl).replaceAll(Matcher.quoteReplacement("\""));// replace "" with "
			// strl = mRegEscSlash.matcher(strl).replaceAll(Matcher.quoteReplacement("\\"));// leave double back slash alone. we still need it.
			strl = mRegEscTab.matcher(strl).replaceAll(Matcher.quoteReplacement("\\t"));	// replace real escape to escape char
			strl = mRegEscEol.matcher(strl).replaceAll(Matcher.quoteReplacement("\\n"));
			
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
	
	private static void printHelp() {
		System.out.println("NlpRunner <src> <dest>");
		System.out.println();
		System.out.println("<src> - the decoded nlp text file.");
		System.out.println("<dest> - the output json file.");
	}
	
	public static void main(String[] args) throws Exception {
		// check parameter
		if (args.length != 2) {
			System.out.println("[ERR] Invalid arguments!");
			printHelp();
			System.exit(1);
		}
		
		// open file stream
		FileInputStream fin = null;
		FileOutputStream fout = null;
		try {
			fin = new FileInputStream(args[0]);
			fout = new FileOutputStream(args[1]);
		} catch (Exception e) {
			if (fin != null) fin.close();
			if (fout != null) fout.close();
			
			System.out.println("[ERR] Fail to open file!");
			printHelp();
			System.exit(1);
		}

		// start lex and parse
		CharStream input = CharStreams.fromStream(fin, StandardCharsets.UTF_8);
		NlpLexer lexer = new NlpLexer(input);
		CommonTokenStream tokens = new CommonTokenStream(lexer);
		NlpParser parser = new NlpParser(tokens);
		
		// walk tree to build json
		ParseTree tree = parser.document();
		ParseTreeWalker walker = new ParseTreeWalker();
		NlpJsonConverter converter = new NlpJsonConverter();
		walker.walk(converter, tree);
		
		// write json
		OutputStreamWriter fw = new OutputStreamWriter(fout, StandardCharsets.UTF_8);
		fw.write(converter.buildJsonString());
		
		// close file stream
		fin.close();
		fw.close();
	}
}
