/**
  *@file ${role.className}.cpp
  *@brief generated code for ${proto.name} packet service
  *@author make_protocol.py
  *@date ${proto.genTime}
  */

#include "${role.className}.h"


${role.className}::${role.className}()
:${proto.cppFileName}(1)  //Initialize with 1 interface
{

}

/**
  *@brief Handler for receiving ping packets
  *@param ${proto.namespace}_ping ptr to incoming ping packet
  *@param ${proto.namespace}_ack ptr to repsonding ack
  *@return PACKET_HANDLED
  */
HandlerStatus_e ${proto.cppFileName}::PingHandler(${proto.camelNamespace()}Packet& ${proto.namespace}_ping, ${proto.camelNamespace()}Packet& ${proto.namespace}_ack)
{
  /* Ack token has already been set as ping token with POLY_ACK_FLAG*/
  uint32_t icd_hash = ${proto.namespace}_ping.getIcd();
  /* assert(icd_hash == ${proto.namespace.upper()}_ICD_VERSION ); */

  return PACKET_HANDLED;
}

/**
  *@brief Handler for receiving ack packets
  *@param ${proto.namespace}_ack ptr to ack
  *@return PACKET_HANDLED
  */
HandlerStatus_e ${proto.cppFileName}::AckHandler(${proto.camelNamespace()}Packet& ${proto.namespace}_ack)
{
  return PACKET_HANDLED;
}

% for packet in proto.packets:
%if not packet.standard:
%if not packet.hasResponse:
/**
  *@brief Handler for receiving ${packet.name} packets
  *@param ${packet.name} incoming ${packet.name} packet
  *@return handling ${proto.namespace}_status
  */
HandlerStatus_e ${proto.cppFileName}::${packet.name}Handler(${proto.camelNamespace()}Packet& ${proto.namespace}_${packet.name})
%else:
/**
  *@brief Handler for receiving ${packet.name} packets
  *@param ${packet.name} incoming ${packet.name} packet
  *@param ${packet.response.name} ${packet.response.name} packet to respond with
  *@return handling ${proto.namespace}_status
  */
HandlerStatus_e ${proto.cppFileName}::${packet.name}Handler(${proto.camelNamespace()}Packet& ${proto.namespace}_${packet.name}, ${proto.camelNamespace()}Packet& ${proto.namespace}_${packet.response.name})
%endif
{
  /*  Get Required Fields in packet */
% for field in packet.fields:
%if field.isRequired:
  //${field.getDeclaration()};  //${field.desc}
%endif
%endfor

% for field in packet.fields:
%if field.isRequired:
  %if field.isArray:
  //${proto.namespace}_get${field.camel()}(${proto.namespace}_${packet.name}, ${field.name});
  %else:
  //${field.name} = ${proto.namespace}_get${field.camel()}(${proto.namespace}_${packet.name});
  %endif
%endif
% endfor
%if packet.hasResponse:
  /*    Set required Fields in response  */
% for field in packet.response.fields:
  //${proto.namespace}_set${field.camel()}(${proto.namespace}_${packet.response.name}, value );  //${field.desc}
%endfor
%endif


  /* NOTE : This function should not be modified! If needed,  It should be overridden in the application code */

  return PACKET_NOT_HANDLED;
}

%endif
% endfor


/**
  *@brief catch-all handler for any packet not yet handled
  *@param ${proto.namespace}_packet ptr to incoming message
  *@param ${proto.namespace}_response ptr to response
  *@return handling ${proto.namespace}_status
  */
HandlerStatus_e ${proto.cppFileName}::defaultHandler( ${proto.camelNamespace()}Packet& ${proto.namespace}Packet, ${proto.camelNamespace()}Packet& ${proto.namespace}Response)
{

  /* NOTE : This function should not be modified, when the callback is needed,
          ${proto.namespace}_default_handler  should be implemented in the user file
  */

  return PACKET_NOT_HANDLED;
}
