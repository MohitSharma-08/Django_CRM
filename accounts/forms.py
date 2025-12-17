from django import forms

class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            base_classes = (
                "w-full px-4 py-2 rounded-lg "
                "border border-gray-300 "
                "bg-white text-gray-900 "
                "placeholder-gray-400 "
                "shadow-sm "
                "transition duration-150 ease-in-out "
                "focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500"
            )

            # Textarea height
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)

            # Select dropdown arrow & spacing
            if isinstance(field.widget, forms.Select):
                base_classes += " pr-10 cursor-pointer"

            # Disabled fields
            if field.disabled:
                base_classes += " bg-gray-100 cursor-not-allowed opacity-70"

            field.widget.attrs.setdefault("class", base_classes)

