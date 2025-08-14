//
// Created by haridev on 8/28/22.
//

#ifndef TAILORFS_INTERFACE_H
#define TAILORFS_INTERFACE_H
/* Internal Headers*/
#include <brahma/interface/interface_utility.h>

/* External Headers */
#include <gotcha/gotcha.h>

#include <memory>
#include <vector>

namespace brahma {
class Interface {
 protected:
  std::shared_ptr<InterfaceUtility> utility;
  std::vector<gotcha_binding_t> bindings;
  std::vector<gotcha_binding_t> unbindings;

 public:
  Interface();
  ~Interface() {}
  char tool_name[64];
  size_t num_bindings;
  int bind_priority;
};
}  // namespace brahma
#endif  // TAILORFS_INTERFACE_H
