package ru.csu.stan.java.ast.treetoxml;

import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.XMLStreamWriter;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerFactoryConfigurationError;

public class XMLWriter {

   // Namespaces
   private static final String GARDENING = "http://com.bdaum.gardening";
   private static final String XHTML = "http://www.w3.org/1999/xhtml";

   public static void main(String[] args) throws XMLStreamException, TransformerConfigurationException, TransformerFactoryConfigurationError  {
      

      // Create an output factory
      XMLOutputFactory xmlof = XMLOutputFactory.newInstance();
      // Set namespace prefix defaulting for all created writers
      xmlof.setProperty("javax.xml.stream.isRepairingNamespaces",Boolean.TRUE);
//      xmlof.setProperty(OutputKeys.INDENT, "yes");
      
      
      // Create an XML stream writer
      XMLStreamWriter xmlw = xmlof.createXMLStreamWriter(System.out);
      
      // Write XML prologue
      xmlw.writeStartDocument();
      // Write a processing instruction
      xmlw.writeProcessingInstruction(
         "xml-stylesheet href='catalog.xsl' type='text/xsl'");
      // Now start with root element
      xmlw.writeCharacters("\n");
      xmlw.writeStartElement("product");
      // Set the namespace definitions to the root element
      // Declare the default namespace in the root element
      xmlw.writeDefaultNamespace(GARDENING);
      // Writing a few attributes
      xmlw.writeAttribute("productNumber","3923-1");
      xmlw.writeAttribute("name","Nightshadow");
      // Declare XHTML prefix
//    xmlw.setPrefix("xhtml",XHTML);
      // Different namespace for description element
      xmlw.writeCharacters("\n");
      xmlw.writeStartElement(XHTML,"description");
      // Declare XHTML namespace in the scope of the description element
//    xmlw.writeNamespace("xhtml",XHTML);
      xmlw.writeCharacters(
         "A tulip of almost black color. \nBlossoms in April & May");
      xmlw.writeEndElement();
      // Shorthand for empty elements
      xmlw.writeCharacters("\n");
      xmlw.writeEmptyElement("supplier");
      xmlw.writeAttribute("name","Floral22");
//    xmlw.writeEndElement();
      // Write document end. This closes all open structures
      xmlw.writeCharacters("\n");
      xmlw.writeEndDocument();
      // Close the writer to flush the output
      xmlw.close();
   }

}