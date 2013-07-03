//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, vJAXB 2.1.10 in JDK 6 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2013.07.01 at 07:24:41 PM YEKT 
//


package ru.csu.stan.java.cfg.jaxb;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlElements;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for Method complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="Method">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;choice maxOccurs="unbounded" minOccurs="0">
 *         &lt;element name="TryExcept" type="{}TryExcept"/>
 *         &lt;element name="TryFinally" type="{}TryFinally"/>
 *         &lt;element name="With" type="{}With"/>
 *         &lt;element name="Block" type="{}Block"/>
 *         &lt;element name="Flow" type="{}Flow"/>
 *         &lt;element name="For" type="{}For"/>
 *         &lt;element name="If" type="{}If"/>
 *         &lt;element name="While" type="{}While"/>
 *       &lt;/choice>
 *       &lt;attribute name="name" type="{http://www.w3.org/2001/XMLSchema}string" />
 *       &lt;attribute name="parent_class" type="{http://www.w3.org/2001/XMLSchema}string" />
 *       &lt;attribute name="label" type="{http://www.w3.org/2001/XMLSchema}string" />
 *       &lt;attribute name="id" type="{http://www.w3.org/2001/XMLSchema}integer" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "Method", propOrder = {
    "tryExceptOrTryFinallyOrWith"
})
public class Method {

    @XmlElements({
        @XmlElement(name = "TryFinally", type = TryFinally.class),
        @XmlElement(name = "If", type = If.class),
        @XmlElement(name = "With", type = With.class),
        @XmlElement(name = "Flow", type = Flow.class),
        @XmlElement(name = "Block", type = Block.class),
        @XmlElement(name = "While", type = While.class),
        @XmlElement(name = "For", type = For.class),
        @XmlElement(name = "TryExcept", type = TryExcept.class)
    })
    protected List<Object> tryExceptOrTryFinallyOrWith;
    @XmlAttribute
    protected String name;
    @XmlAttribute(name = "parent_class")
    protected String parentClass;
    @XmlAttribute
    protected String label;
    @XmlAttribute
    protected BigInteger id;

    /**
     * Gets the value of the tryExceptOrTryFinallyOrWith property.
     * 
     * <p>
     * This accessor method returns a reference to the live list,
     * not a snapshot. Therefore any modification you make to the
     * returned list will be present inside the JAXB object.
     * This is why there is not a <CODE>set</CODE> method for the tryExceptOrTryFinallyOrWith property.
     * 
     * <p>
     * For example, to add a new item, do as follows:
     * <pre>
     *    getTryExceptOrTryFinallyOrWith().add(newItem);
     * </pre>
     * 
     * 
     * <p>
     * Objects of the following type(s) are allowed in the list
     * {@link TryFinally }
     * {@link If }
     * {@link With }
     * {@link Flow }
     * {@link Block }
     * {@link While }
     * {@link For }
     * {@link TryExcept }
     * 
     * 
     */
    public List<Object> getTryExceptOrTryFinallyOrWith() {
        if (tryExceptOrTryFinallyOrWith == null) {
            tryExceptOrTryFinallyOrWith = new ArrayList<Object>();
        }
        return this.tryExceptOrTryFinallyOrWith;
    }

    /**
     * Gets the value of the name property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getName() {
        return name;
    }

    /**
     * Sets the value of the name property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setName(String value) {
        this.name = value;
    }

    /**
     * Gets the value of the parentClass property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getParentClass() {
        return parentClass;
    }

    /**
     * Sets the value of the parentClass property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setParentClass(String value) {
        this.parentClass = value;
    }

    /**
     * Gets the value of the label property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getLabel() {
        return label;
    }

    /**
     * Sets the value of the label property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setLabel(String value) {
        this.label = value;
    }

    /**
     * Gets the value of the id property.
     * 
     * @return
     *     possible object is
     *     {@link BigInteger }
     *     
     */
    public BigInteger getId() {
        return id;
    }

    /**
     * Sets the value of the id property.
     * 
     * @param value
     *     allowed object is
     *     {@link BigInteger }
     *     
     */
    public void setId(BigInteger value) {
        this.id = value;
    }

}